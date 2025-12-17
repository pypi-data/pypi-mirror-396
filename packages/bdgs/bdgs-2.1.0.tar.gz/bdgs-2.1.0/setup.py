from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name="bdgs",
    version="2.1.0",
    packages=find_packages(),
    install_requires=[
        'opencv-python~=4.11.0.86',
        'numpy~=2.1.3',
        'tensorflow-cpu~=2.19.0',
        'scikit-learn~=1.6.1',
        "keras~=3.9.2",
        'scikit-image~=0.25.2',
        'silence-tensorflow~=1.2.3'
    ],
    include_package_data=True,
    package_data={
        'bdgs_trained_models': ['*'],
    },
    py_modules=['definitions'],
    author="marcinbator",
    author_email="marcinbator.ofc@gmail.com",
    description="Static gestures recognition tool",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.11',
)
