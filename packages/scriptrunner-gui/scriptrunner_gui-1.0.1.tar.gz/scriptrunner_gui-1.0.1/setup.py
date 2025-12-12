import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setuptools.setup(
    name="scriptrunner-gui",
    version="1.0.1",
    author="Nghia Vo",
    author_email="nvo@bnl.gov",
    description="GUI software for rendering arguments of CLI Python scripts and scheduling runs.",
    long_description=README,
    long_description_content_type="text/markdown",
    keywords=['Script rendering'],
    url="https://github.com/algotom/scriptrunner",
    download_url="https://github.com/algotom/scriptrunner.git",
    license="Apache 2.0",
    platforms="Any",
    packages=setuptools.find_packages(include=["scriptrunner", "scriptrunner.*"]),
    package_data={"scriptrunner.assets": ["ScriptRunner_icon.png"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Scientific/Engineering"
    ],
    entry_points={'console_scripts': ['scriptrunner = scriptrunner.main:main']},
    python_requires='>=3.9',
)
