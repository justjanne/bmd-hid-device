from setuptools import setup, find_packages

name = "bmd-hid-device"
description = "library to provide access to blackmagicdesign hid devices"

setup(name=name,
      version="0.1.9",
      description=description,
      url="https://github.com/justjanne/bmd-hid-device",
      project_urls={
          "GitHub": "https://github.com/justjanne/bmd-hid-device",
          "Issue tracker": "https://github.com/justjanne/bmd-hid-device/issues",
      },
      install_requires=["hid"],
      packages=find_packages(),
      package_data={'bmd_hid_device': ['py.typed']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
