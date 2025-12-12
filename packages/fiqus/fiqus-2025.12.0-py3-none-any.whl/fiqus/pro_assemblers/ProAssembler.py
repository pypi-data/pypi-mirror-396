from fiqus.pro_templates import combined
from jinja2 import Environment, FileSystemLoader
import numpy as np
import os


class ASS_PRO:
    def __init__(self, file_base_path, naming_conv=None):
        """
        Class for generating pro templates
        :param file_base_path: this is a full path to a folder with the model and includes model name, but without extension
        :param naming_conv: a dictionary with naming convention for regions in .pro file. Optional parameter, as a default below is used, but it could be overwritten if needed.
        """
        self.file_base_path = file_base_path
        if not naming_conv:
            self.naming_conv = {'omega': 'Omega', 'terms': 'Terms', 'bd': 'Bd', 'cond': '_c', 'powered': '_p', 'induced': '_i', 'air': '_a', 'line': 'Line'}
        else:
            self.naming_conv = naming_conv

    def assemble_combined_pro(self, template, dm, rm=None, mf=None, ps=None, ed=None, mp=None, rm_EM=None, rm_TH=None, rc=None,
                              BH_curves_path: str = '', external_templates_paths: list = None):
        """
        Generates model .pro file from .pro template and regions model (rm)
        :param external_templates_paths: list of paths to external templates directories
        :param BH_curves_path: path of the BH curves pro file
        :param template: .pro template file name
        :param rm: regions model data structure (yaml loaded to regions data model)
        :param rm_EM: regions model data structure for electromagnetics (yaml loaded to regions data model)
        :param rm_TH: regions model data structure for thermal (yaml loaded to regions data model)
        :param rc: regions coordinates data structure
        :param dm: data model structure
        :param mf: full path to mesh file to be used in solution
        :param ps: previous solution folder (this is used by CWS for co-simulation run)
        :param ed: excitation dictionary with lists (e.g. times and currents) to be used in a pro file (e.g. transient simulation)
        :param mp: material properties data structure
        :return: None. Generates .pro file and saves it on disk in the model folder under model_name.pro
        """
        external_templates_paths = external_templates_paths if external_templates_paths else []
        loader = FileSystemLoader([os.path.dirname(combined.__file__)] + external_templates_paths)
        env = Environment(loader=loader, variable_start_string='<<', variable_end_string='>>',
                          trim_blocks=True, lstrip_blocks=True, extensions=['jinja2.ext.do'])
        env.globals.update(set=set, str=str, int=int, float=float, zip=zip, enumerate=enumerate, list=list,
                           len=len, isinstance=isinstance, arange=np.arange, Pi=np.pi)  # this is to pass python zip function to the template, as normally it is not available. It should work for passing any python function that is not available in .pro template.
        pro_template = env.get_template(template)
        output_from_parsed_template = pro_template.render(BHcurves=BH_curves_path, dm=dm, rm=rm, mf=mf, nc=self.naming_conv,
                                                          ps=ps, ed=ed, mp=mp, rm_EM=rm_EM, rm_TH=rm_TH, rc=rc)
        with open(f"{self.file_base_path}.pro", "w") as tf:
            tf.write(output_from_parsed_template)

    def assemble_separate_pro(self, template, rm, dm, BH_curves_path: str = ''):
        """
        This function is not developed yet.
        """
        pass
