from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name='caerp_oidc_client',
    version='2025.1.1',
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    include_package_data=True,
    license='GPLv3',
    url="https://framagit.org/caerp/caerp_oidc_client",
    description="OpenID Connect client for CAERP",
    author='Gaston Tjebbes - Majerti',
    author_email='tech@majerti.fr',
    install_requires=["pyjwt", "requests"],
    python_requires=">=3.9, <4",
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Framework :: Pyramid',
    ],
)
