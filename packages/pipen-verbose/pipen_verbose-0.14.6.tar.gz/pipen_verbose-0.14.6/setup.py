# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['pipen_verbose']
install_requires = \
['pipen==0.17.*']

entry_points = \
{'pipen': ['verbose = pipen_verbose:PipenVerbose']}

setup_kwargs = {
    'name': 'pipen-verbose',
    'version': '0.14.6',
    'description': 'Add verbosal information in logs for pipen.',
    'long_description': '# pipen-verbose\n\nAdd verbosal information in logs for [pipen][1].\n\n## Additional information\n\n- Following process properties if not `None` and different from pipeline-level configurations: `scheduler`, `lang`, `forks`, `cache`, `dirsig`, `size`, `template`\n- Ellapsed time for a process. Note that this is time ellapsed from process initialization to completion, no matter the jobs are cached or not, so this is not the real running time for the jobs.\n- Process `envs` if set.\n- Computed input data for processes.\n- The indices of failed jobs if any.\n- The stderr, paths to script, stdout file, stderr file, of the first failed jobs if any.\n- The input/output data of the first job.\n\n## Installation\n\n```\npip install -U pipen-verbose\n```\n\n## Enabling/Disabling the plugin\n\nThe plugin is registered via entrypoints. It\'s by default enabled. To disable it:\n`plugins=[..., "no:verbose"]`, or uninstall this plugin.\n\n## Usage\n\n`example.py`\n```python\nfrom pipen import Proc, Pipen\n\nclass Process(Proc):\n    input = \'a\'\n    input_data = range(10)\n    output = \'b:file:a.txt\'\n    cache = False\n    script = \'echo {{in.a}} > {{out.b}}\'\n\nPipen().run(Process)\n```\n\n```\n> python example.py\n[09/12/21 22:57:01] I main                   _____________________________________   __\n[09/12/21 22:57:01] I main                   ___  __ \\___  _/__  __ \\__  ____/__  | / /\n[09/12/21 22:57:01] I main                   __  /_/ /__  / __  /_/ /_  __/  __   |/ /\n[09/12/21 22:57:01] I main                   _  ____/__/ /  _  ____/_  /___  _  /|  /\n[09/12/21 22:57:01] I main                   /_/     /___/  /_/     /_____/  /_/ |_/\n[09/12/21 22:57:01] I main\n[09/12/21 22:57:01] I main                                version: 0.1.0\n[09/12/21 22:57:01] I main\n[09/12/21 22:57:01] I main    ╭═════════════════════════════ PIPEN-0 ══════════════════════════════╮\n[09/12/21 22:57:01] I main    ║  # procs          = 1                                              ║\n[09/12/21 22:57:01] I main    ║  plugins          = [\'main\', \'verbose-0.0.1\']                      ║\n[09/12/21 22:57:01] I main    ║  profile          = default                                        ║\n[09/12/21 22:57:01] I main    ║  outdir           = ./Pipen-output                                 ║\n[09/12/21 22:57:01] I main    ║  cache            = True                                           ║\n[09/12/21 22:57:01] I main    ║  dirsig           = 1                                              ║\n[09/12/21 22:57:01] I main    ║  error_strategy   = ignore                                         ║\n[09/12/21 22:57:01] I main    ║  forks            = 1                                              ║\n[09/12/21 22:57:01] I main    ║  lang             = bash                                           ║\n[09/12/21 22:57:01] I main    ║  loglevel         = info                                           ║\n[09/12/21 22:57:01] I main    ║  num_retries      = 3                                              ║\n[09/12/21 22:57:01] I main    ║  plugin_opts      = {}                                             ║\n[09/12/21 22:57:01] I main    ║  plugins          = None                                           ║\n[09/12/21 22:57:01] I main    ║  scheduler        = local                                          ║\n[09/12/21 22:57:01] I main    ║  scheduler_opts   = {}                                             ║\n[09/12/21 22:57:01] I main    ║  submission_batch = 8                                              ║\n[09/12/21 22:57:01] I main    ║  template         = liquid                                         ║\n[09/12/21 22:57:01] I main    ║  template_opts    = {}                                             ║\n[09/12/21 22:57:01] I main    ║  workdir          = ./.pipen                                       ║\n[09/12/21 22:57:01] I main    ╰════════════════════════════════════════════════════════════════════╯\n[09/12/21 22:57:02] I main\n[09/12/21 22:57:02] I main    ╭═════════════════════════════ Process ══════════════════════════════╮\n[09/12/21 22:57:02] I main    ║ Undescribed                                                        ║\n[09/12/21 22:57:02] I main    ╰════════════════════════════════════════════════════════════════════╯\n[09/12/21 22:57:02] I main    Process: Workdir: \'.pipen/pipen-0/process\'\n[09/12/21 22:57:02] I main    Process: <<< [START]\n[09/12/21 22:57:02] I main    Process: >>> [END]\n[09/12/21 22:57:02] I verbose Process: cache: False\n[09/12/21 22:57:02] I verbose Process: size : 10\n[09/12/21 22:57:02] I verbose Process: [0/9] in.a: 0\n[09/12/21 22:57:02] I verbose Process: [0/9] out.b:\n                      /home/pwwang/github/pipen-verbose/Pipen-output/Process/0/a.txt\n[09/12/21 22:57:04] I verbose Process: Time elapsed: 00:00:02.043s\n[09/12/21 22:57:04] I main\n```\n\n[1]: https://github.com/pwwang/pipen\n',
    'author': 'pwwang',
    'author_email': 'pwwang@pwwang.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/pwwang/pipen-verbose',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
