from setuptools import setup, find_packages

setup(
    name="mfsapi",
    version="0.1.1",
    description="SSAPI — Fully free and extensible server/client skeleton",
    long_description="SSAPI — Simple Server API",
    long_description_content_type="text/markdown",
    author="maksalmaz",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    zip_safe=False,
)