

import pandas as pd
from xmle import Elem
import matplotlib.figure
import io
import base64
from PIL import Image
try:
    import xlsxwriter
except ImportError:
    xlsxwriter = None
    _XlsxWriter = object
else:
    from pandas.io.excel._xlsxwriter import _XlsxWriter

class ExcelWriter(_XlsxWriter):

    def __init__(self, *args, model=None, data_statistics=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.head_fmt = self.book.add_format({'bold': True})
        if model is not None:
            self.add_model(model, data_statistics=data_statistics)
        self.sheet_startrow = {}

    def add_model(self, model, data_statistics=True):

        model.pfo().to_excel(self, sheet_name="Parameters")

        if data_statistics:
            from .statistics import statistics_for_dataframe

            if model.dataframes.data_co is not None:
                statistics_for_dataframe(model.dataframes.data_co).to_excel(self, sheet_name="CO Data")
            if model.dataframes.data_ca is not None:
                statistics_for_dataframe(model.dataframes.data_ca).to_excel(self, sheet_name="CA Data")
            if model.dataframes.data_ce is not None:
                statistics_for_dataframe(model.dataframes.data_ce).to_excel(self, sheet_name="CE Data")
            if model.dataframes.data_ch is not None and model.dataframes.data_av is not None:
                model.dataframes.choice_avail_summary(graph=model.graph).to_excel(self, sheet_name="Choices")

    def add_worksheet(self, name, force=False):

        if not force and name in self.sheets:
            return self.sheets[name]

        s = None
        try:
            s = self.book.add_worksheet(name)
        except xlsxwriter.exceptions.DuplicateWorksheetName:
            i = 2
            while s is None:
                try:
                    s = self.book.add_worksheet(f"{name}{i}")
                except xlsxwriter.exceptions.DuplicateWorksheetName:
                    i += 1
                    if i > 99:
                        raise
        self.sheets[name] = s
        return s

    def add_content_tab(self, content, sheetname, heading=None, startrow=None):

        if startrow is None:
            startrow = self.sheet_startrow.get(sheetname, 0)
        worksheet = self.add_worksheet(sheetname)

        content_in = content
        success = False

        if isinstance(content, pd.DataFrame):
            if heading is not None:
                worksheet.write(startrow, 0, heading, self.head_fmt)
                startrow += 1
            content.to_excel(self, sheet_name=worksheet.name, startrow=2 if heading is not None else 0)
            startrow += len(content) + content.columns.nlevels
            if content.index.name:
                startrow += 1
            startrow += 2 # gap
            success = True

        # Render matplotlib.Figure into an Elem
        if not success and 'matplotlib' in str(type(content)):
            if isinstance(content, matplotlib.figure.Figure):
                try:
                    content = Elem.from_figure(content, format='png', dpi='figure')
                except:
                    pass

        # Extract PNG data from Elem if found there
        if not success and isinstance(content, Elem):
            _v = content.find('img')
            if _v is not None:
                try:
                    _v = _v.attrib['src']
                except:
                    pass
                else:
                    if isinstance(_v, str) and _v[:22] == 'data:image/png;base64,':
                        _v = io.BytesIO(base64.standard_b64decode(_v[22:]))
                        pixel_width, pixel_height = Image.open(_v).size
                        if heading is not None:
                            worksheet.write(startrow, 0, heading, self.head_fmt)
                            startrow += 1
                        worksheet.insert_image(startrow, 0, f'image-{sheetname}.png', {'image_data': _v})
                        startrow += (pixel_height // 15) + 3
                        success = True

        if not success:
            import warnings
            warnings.warn(f'content not written to sheet {sheetname}')

        self.sheet_startrow[worksheet.name] = startrow
        return content_in

    def save(self, makedirs=True, overwrite=False):
        if makedirs:
            import os
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

        if not overwrite:
            from xmle.file_util import archive_existing_file
            try:
                archive_existing_file(self.path, archive_path=None, tag='creation')
            except FileNotFoundError:
                pass

        super().save()

def _make_excel_writer(model, filename, data_statistics=True):
    xl = ExcelWriter(filename, model=model, data_statistics=data_statistics)
    return xl

if xlsxwriter is not None:
    from .. import Model
    Model.to_xlsx = _make_excel_writer



def image_dims():
    from PIL import Image

    im = Image.open('whatever.png')
    width, height = im.size