from .__metadata__ import __version__, __description__, __build__, __name__
from .GMXvg import GMXvg
from UtilityLib import CMDLib, OS, EntityPath

_cli_settings = {
    "path_base"        : (['-b'], None, OS.getcwd(), 'Provide base directory to run the process.', {}),
    "patterns_xvg"     : (['-p'], "*", ["*.xvg"], 'File patterns to match XVG files.', {}),
    "path_input_dirs"  : (['-i'], "*", None, 'Input directories containing XVG files.', {}),
    "export_ext"       : (['-e'], "*", ["jpg"], 'Export file extensions for plots.', {}),
    "export_dpi"       : (['-d'], "*", ["300"], 'DPI settings for exported plots.', {}),
    "flag_plot_mean"   : (['-m'], None, "Y", 'Flag to plot mean line (Y/N).', {}),
    "flag_plot_std"    : (['-s'], None, None, 'Flag to plot standard deviation lines (Y/N).', {}),
    "flag_export_csv"  : (['-c'], None, None, 'Flag to export results as CSV (Y/N).', {}),
    "flag_export_plot" : (['-f'], None, "Y", 'Flag to export plots (Y/N).', {}),
    "flag_cleanup"     : (['-x'], None, None, 'Flag to cleanup generated files (Y/N).', {}),
    "csv_filename"     : (['-o'], "*", "XVG-Plot-Values.csv", 'Output CSV filename for results.', {}),
  }

def xvgplot_cli():
  global _cli_settings
  _args = CMDLib.get_registered_args(_cli_settings, version=f"{__name__}-{__version__}")
  _m = GMXvg(**_args)
  _m.plot()

def xvgplot_cli_test():
  # Setup test example
  global _cli_settings
  _test_examples    = EntityPath(__file__).parent(1) / 'docs/example-xvgs'
  _test_destination = EntityPath('~/Desktop/GMXvg-Example-XVGs').resolved()
  if _test_destination.exists():
    _test_destination.delete(False)
  _test_examples.copy(_test_destination)

  _args              = CMDLib.get_registered_args(_cli_settings, version=f"{__name__}-{__version__}")
  _args['path_base'] = _test_destination.full_path

  _m = GMXvg(**_args)
  _m.plot()
