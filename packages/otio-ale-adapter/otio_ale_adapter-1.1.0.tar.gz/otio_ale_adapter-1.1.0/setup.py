from setuptools import setup

setup(
    name='otio-ale-adapter',
    version='1.1.0',
    description='OpenTimelineIO ALE Adapter',
    long_description='# OpenTimelineIO ALE Adapter\n[![Build Status](https://github.com/OpenTimelineIO/otio-ale-adapter/actions/workflows/ci.yaml/badge.svg)](https://github.com/OpenTimelineIO/otio-ale-adapter/actions/workflows/ci.yaml)\n![Dynamic YAML Badge](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOpenTimelineIO%2Fotio-ale-adapter%2Fmain%2F.github%2Fworkflows%2Fci.yaml&query=%24.jobs%5B%22test-plugin%22%5D.strategy.matrix%5B%22otio-version%22%5D&label=OpenTimelineIO)\n![Dynamic YAML Badge](https://img.shields.io/badge/dynamic/yaml?url=https%3A%2F%2Fraw.githubusercontent.com%2FOpenTimelineIO%2Fotio-ale-adapter%2Fmain%2F.github%2Fworkflows%2Fci.yaml&query=%24.jobs%5B%22test-plugin%22%5D.strategy.matrix%5B%22python-version%22%5D&label=Python)\n\nThe `ale` adapter is part of OpenTimelineIO\'s contrib adapter plugins.\n\n\n# Adapter Feature Matrix\n\nThe following features of OTIO are supported by the `ale` adapter:\n\n|Feature                  | Support |\n|-------------------------|:-------:|\n|Single Track of Clips    | ✔       |\n|Multiple Video Tracks    | ✔       |\n|Audio Tracks & Clips     | ✔       |\n|Gap/Filler               | ✖       |\n|Markers                  | ✖       |\n|Nesting                  | ✔       |\n|Transitions              | ✖       |\n|Audio/Video Effects      | ✖       |\n|Linear Speed Effects     | ✖       |\n|Fancy Speed Effects      | ✖       |\n|Color Decision List      | N/A     |\n|Image Sequence Reference | ✖       |\n\n# Adapter specific arguments\nThe ALE adapter adds a couple of optional arguments to the `read_from_string()` function\n>read_from_string(input_str, **fps=24**, **ale_name_column_key=\'Name\'**)  \n\nThe ALE adapter adds a couple of optional arguments to the `write_to_string()` function\n>write_to_string(input_otio, **columns=None**, **fps=None**, **video_format=None**)\n\n# License\n\nOpenTimelineIO and the "ale" adapter are open source software.\nPlease see the [LICENSE](LICENSE) for details.\n\nNothing in the license file or this project grants any right to use Pixar or\nany other contributor’s trade names, trademarks, service marks, or product names.\n\n# Contributions\n\nIf you want to contribute to the project,\nplease see: https://opentimelineio.readthedocs.io/en/latest/tutorials/contributing.html  \nPlease also read up on [testing your code](https://github.com/OpenTimelineIO/otio-plugin-template#testing-your-plugin-during-development) \nin the "getting started" section of the OpenTimelineIO plugin template repository.\n\n# Contact\n\nFor more information, please visit http://opentimeline.io/\nor https://github.com/AcademySoftwareFoundation/OpenTimelineIO\nor join our discussion forum: https://lists.aswf.io/g/otio-discussion\n',
    author_email='Contributors to the OpenTimelineIO project <otio-discussion@lists.aswf.io>',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'opentimelineio>=0.18.1',
    ],
    entry_points={
        'opentimelineio.plugins': [
            'otio_ale_adapter = otio_ale_adapter',
        ],
    },
    packages=[
        'otio_ale_adapter',
    ],
    package_dir={'': 'src'},
)
