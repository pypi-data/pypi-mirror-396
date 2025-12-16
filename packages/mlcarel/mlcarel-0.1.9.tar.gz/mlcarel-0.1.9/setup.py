from setuptools import setup,find_packages
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mlcarel",
    version="0.1.9",
    description="Software for Generalized Matrix-based LCA and Reliability Based LCA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shinsuke Sakai",
    author_email='sakaishin0321@gmail.com',
    url='https://github.com/ShinsukeSakai0321/PyMLCA',
    packages=find_packages(),
    install_requires=[
        "pandas>=2.2.3",
        "pyDOE>=0.3.8",
        "scikit-learn>=1.6.1",
        "LimitState>=0.0.2",
        # 他に必要なパッケージをここに書く
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    package_data={'':['*.csv']},
    include_package_data=True,
    python_requires='>=3.6',
)