# cython: language_level=3, embedsignature=True

from ..general_precision cimport *
from ..dataframes cimport DataFrames
from .linear cimport LinearFunction_C, DictOfLinearFunction_C
from .parameter_frame cimport ParameterFrame



cdef class Model5c(ParameterFrame):

	cdef public:
		DictOfLinearFunction_C _utility_co
		LinearFunction_C _utility_ca
		LinearFunction_C _quantity_ca

	cdef:
		DataFrames _dataframes
		object _dataservice

		object _quantity_scale
		object _logsum_parameter
		object rename_parameters

		str    _choice_ca_var
		object _choice_co_vars
		str    _choice_co_code
		str    _weight_co_var
		str    _availability_var
		object _availability_co_vars

		bint _is_clone

		object _graph

		object _possible_overspecification

		object _most_recent_estimation_result
		double _cached_loglike_null
		double _cached_loglike_constants_only
		double _cached_loglike_best

		int _n_threads

		object dashboard