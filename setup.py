import setuptools
from setuptools import setup, Extension
import glob, time, platform, os, sysconfig, sys, shutil, io

VERSION = '3.1.48'



if os.environ.get('READTHEDOCS', None) == 'True':
	# hack for building docs on rtfd
	def read(*filenames, **kwargs):
		encoding = kwargs.get('encoding', 'utf-8')
		sep = kwargs.get('sep', '\n')
		buf = []
		for filename in filenames:
			with io.open(filename, encoding=encoding) as f:
				buf.append(f.read())
		return sep.join(buf)

	long_description = read('README.rst')
	
	setup(name='larch',
		  version=VERSION,
		  package_dir = {'larch': 'py'},
		  packages=['larch', 'larch.examples', 'larch.version', 'larch.util', 'larch.util.optimize', 'larch.model_reporter'],
		  url='http://larch.readthedocs.org',
		  download_url='http://github.com/jpn--/larch',
		  author='Jeffrey Newman',
		  author_email='jeff@newman.me',
		  description='A framework for estimating and applying discrete choice models.',
		  long_description=long_description,
		  license = 'GPLv3',
		  classifiers = [
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
			'Programming Language :: Python :: 3',
			'Programming Language :: Python :: 3.4',
			'Programming Language :: Python :: 3.5',
			'Operating System :: MacOS :: MacOS X',
			'Operating System :: Microsoft :: Windows',
		  ],
		 )


else:

	usedir = os.path.dirname(__file__)
	if sys.path[0] != usedir:
		sys.path.insert(0, usedir)

	def file_at(*arg):
		return os.path.join(usedir, *arg)

	def incl(*arg):
		return '-I'+os.path.join(usedir, *arg)

	def read(*filenames, **kwargs):
		encoding = kwargs.get('encoding', 'utf-8')
		sep = kwargs.get('sep', '\n')
		buf = []
		for filename in filenames:
			with io.open(filename, encoding=encoding) as f:
				buf.append(f.read())
		return sep.join(buf)

	long_description = read(file_at('README.rst'))
		

	import numpy

	if platform.system() == 'Darwin':
		os.environ['LDFLAGS'] = '-framework Accelerate'
		os.environ['CLANG_CXX_LIBRARY'] = 'libc++'
		os.environ['CLANG_CXX_LANGUAGE_STANDARD'] = 'gnu++0x'

	# To update the version, run `git tag -a 3.1.1-JAN2015 -m'version 3.1.1, January 2015'`



	compiletime = time.strftime("%A %B %d %Y - %I:%M:%S %p")


	elm_cpp_dirs = ['etk', 'model', 'data', 'sherpa', 'vascular']

	elm_cpp_fileset = set()
	for elm_cpp_dir in elm_cpp_dirs:
		#elm_cpp_fileset |= set(glob.glob('src/{}/*.cpp'.format(elm_cpp_dir)))
		elm_cpp_fileset |= set(glob.glob(file_at('src',elm_cpp_dir,'*.cpp')))


	elm_cpp_files = list(elm_cpp_fileset)

	for elm_cpp_dir in elm_cpp_dirs:
		#elm_cpp_fileset |= set(glob.glob('src/{}/*.h'.format(elm_cpp_dir)))
		elm_cpp_fileset |= set(glob.glob(file_at('src',elm_cpp_dir,'*.h')))

	elm_cpp_h_files = list(elm_cpp_fileset)

	from setup_common import lib_folder, shlib_folder, temp_folder




	if platform.system() == 'Darwin':
		openblas = None
		gfortran = None
		mingw64_libs = []
		local_swig_opts = []
		local_libraries = []
		local_library_dirs = []
		local_includedirs = []
		local_macros = [('I_AM_MAC','1'), ('SQLITE_ENABLE_RTREE','1'), ]
		local_extra_compile_args = ['-std=gnu++11', '-w', '-arch', 'i386', '-arch', 'x86_64']# +['-framework', 'Accelerate']
		local_apsw_compile_args = ['-w']
		local_extra_link_args =   ['-framework', 'Accelerate']
		local_data_files = [('/usr/local/bin', [file_at('bin','larch')]), ]
		local_sqlite_extra_postargs = []
		dylib_name_style = "lib{}.so"
		DEBUG = False
	elif platform.system() == 'Windows':
		#old openblas = 'OpenBLAS-v0.2.9.rc2-x86_64-Win', 'lib', 'libopenblas.dll'
		openblas = 'OpenBLAS-v0.2.15-Win64-int32', 'lib', 'libopenblas.dll'
		#gfortran = 'OpenBLAS-v0.2.9.rc2-x86_64-Win', 'lib', 'libgfortran-3.dll'
		gfortran = 'OpenBLAS-v0.2.15-Win64-int32', 'lib', 'libgfortran-3.dll'
		mingw64_path = 'OpenBLAS-v0.2.15-Win64-int32', 'lib',
		mingw64_dlls = ['libgfortran-3', 'libgcc_s_seh-1', 'libquadmath-0']
		mingw64_libs = [i+'.dll' for i in mingw64_dlls]
		local_swig_opts = []
		local_libraries = ['PYTHON35','libopenblas',]+mingw64_dlls+['PYTHON35',]
		local_library_dirs = [
			'Z:/Larch/{0}/{1}'.format(*openblas),
		#	'C:\\local\\boost_1_56_0\\lib64-msvc-10.0',
			]
		local_includedirs = [
			'./{0}/include'.format(*openblas),
		#	'C:/local/boost_1_56_0',
			 ]
		local_macros = [('I_AM_WIN','1'),  ('SQLITE_ENABLE_RTREE','1'), ]
		local_extra_compile_args = ['/EHsc', '/W0', ]
		#  for debugging...
		#	  extra_compile_args=['/Zi' or maybe '/Z7' ?],
		#     extra_link_args=[])
		local_apsw_compile_args = ['/EHsc']
		local_extra_link_args =    ['/DEBUG']
		local_data_files = []
		local_sqlite_extra_postargs = ['/IMPLIB:' + os.path.join(shlib_folder(), 'larchsqlite.lib'), '/DLL',]
		dylib_name_style = "{}.dll"
		DEBUG = False
	#	raise Exception("TURN OFF multithreading in OpenBLAS")
	else:
		openblas = None
		gfortran = None
		mingw64_libs = []
		local_swig_opts = []
		local_libraries = []
		local_library_dirs = []
		local_includedirs = []
		local_macros = [('I_AM_LINUX','1'),  ('SQLITE_ENABLE_RTREE','1'), ]
		local_extra_compile_args = []
		local_apsw_compile_args = []
		local_extra_link_args =    []
		local_data_files = []
		local_sqlite_extra_postargs = []
		dylib_name_style = "{}.so"
		DEBUG = False


	from setup_sqlite import build_sqlite
	build_sqlite()


#	shared_libs = [
#	('larchsqlite', ['sqlite/sqlite3.c','sqlite/haversine.c','sqlite/bonus.c'] ,sqlite3_exports,  local_sqlite_extra_postargs, []),
#	]
#
#
	from distutils.ccompiler import new_compiler

	# Create compiler with default options
	c = new_compiler()
	c.add_include_dir("./sqlite")
#
#	for name, source, exports, extra_postargs, extra_preargs in shared_libs:
#		
#		if not isinstance(source,list):
#			source = [source,]
#		
#		need_to_update = False
#		for eachsource in source:
#			try:
#				need_to_update = need_to_update or (os.path.getmtime(eachsource) > os.path.getmtime(os.path.join(libdir, dylib_name_style.format(name))))
#			except FileNotFoundError:
#				need_to_update = True
#
#		# change dynamic library install name
#		if platform.system() == 'Darwin':
#			extra_postargs += ['-install_name', '@loader_path/{}'.format(c.library_filename(name,'shared'))]
#			extra_preargs  += ['-arch', 'i386', '-arch', 'x86_64']
#
#		if need_to_update:
#			# Compile into .o files
#			objects = c.compile(source, extra_preargs=extra_preargs, debug=DEBUG, macros=local_macros, output_dir=temp_folder())
#			# Create shared library
#			c.link_shared_lib(objects, name, output_dir=libdir, export_symbols=exports, extra_preargs=extra_preargs, extra_postargs=extra_postargs, debug=DEBUG)


	if openblas is not None:
		shutil.copyfile(os.path.join('Z:/Larch',*openblas), os.path.join(shlib_folder(),openblas[-1]))
	for dll in mingw64_libs:
		shutil.copyfile(os.path.join('Z:/Larch',*(mingw64_path+(dll,))), os.path.join(shlib_folder(),dll))




	core = Extension('larch._core',
					 [file_at('src/swig/elmcore.i'),] + elm_cpp_files,
					 swig_opts=['-modern', '-py3',
								#'-I../include',
								'-v', '-c++', '-outdir', file_at('py'),
								#'-I../include',
								incl('src/etk'),
								incl('src/model'),
								incl('src/data'),
								incl('src/sherpa'),
								incl('src/vascular'),
								incl('src/version'),
								incl('src/swig'),
								incl('sqlite'), ] + local_swig_opts,
					 libraries=local_libraries+['larchsqlite', ],
					 library_dirs=local_library_dirs+[shlib_folder(),],
					 define_macros=local_macros,
					 include_dirs=local_includedirs + [numpy.get_include(),
													   file_at('src'),
													   file_at('src/etk'),
													   file_at('src/model'),
													   file_at('src/data'),
													   file_at('src/sherpa'),
													   file_at('src/vascular'),
													   file_at('src/version'),
													   file_at('src/swig'),
													   file_at('sqlite'), ],
					 extra_compile_args=local_extra_compile_args,
					 extra_link_args=local_extra_link_args,
					 depends=[file_at('src/swig/elmcore.i'),] + elm_cpp_h_files,
					 )

	apsw_extra_link_args = []
	if platform.system() == 'Darwin':
		apsw_extra_link_args += ['-install_name', '@loader_path/{}'.format(c.library_filename('apsw','shared'))]


	apsw = Extension('larch.apsw',
					 [file_at('sqlite/apsw/apsw.c'),],
					 libraries=['larchsqlite', ],
					 library_dirs=[shlib_folder(),],
					 define_macros=local_macros+[('EXPERIMENTAL','1')],
					 include_dirs= [ file_at('sqlite'), file_at('sqlite/apsw'), ],
					 extra_compile_args=local_apsw_compile_args,
	#				 extra_link_args=apsw_extra_link_args,
					 )


	import build_configuration
	build_configuration.write_build_info(build_dir=lib_folder(), packagename="larch")




	setup(name='larch',
		  version=VERSION,
		  package_dir = {'larch': file_at('py')},
		  packages=['larch', 'larch.examples', 'larch.test', 'larch.version', 'larch.util', 'larch.model_reporter', 'larch.util.optimize',],
		  ext_modules=[core, apsw, ],
		  package_data={'larch':['data_warehouse/*.sqlite', 'data_warehouse/*.csv', 'data_warehouse/*.csv.gz', 'data_warehouse/*.h5']},
		  data_files=local_data_files,
		  install_requires=[
							"numpy >= 1.10",
							"scipy >= 0.14.0",
							"pandas >= 0.14.1",
							"tables >= 3.2.2"
						],
		  extras_require = {
			'docx':  ["python-docx >= 0.8.5",],
			'test': ["nose >= 1.3",],
			'network': ["networkx >= 1.10",],
			'graphing': ["pygraphviz >= 1.3", "matplotlib >= 1.5", ],
			'docs': ["sphinx >= 1.2.3", "sphinxcontrib-napoleon >= 0.4",],
		  },
		  url='http://larch.readthedocs.org',
		  download_url='http://github.com/jpn--/larch',
		  author='Jeffrey Newman',
		  author_email='jeff@newman.me',
		  description='A framework for estimating and applying discrete choice models.',
		  long_description=long_description,
		  license = 'GPLv3',
		  classifiers = [
			'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
			'Programming Language :: Python :: 3',
			'Programming Language :: Python :: 3.4',
			'Programming Language :: Python :: 3.5',
			'Operating System :: MacOS :: MacOS X',
			'Operating System :: Microsoft :: Windows',
		  ],
		 )


