from setuptools import setup, find_packages

setup(
    name="COOLBOOY",
    version="1.2.1",
    author="coolbooy",
    author_email="coolbooy@gmail.com",
    description="COOLBOOY-Multi-Provider AI Assistant for developers and power users.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=["COOLBOOY"],
    install_requires=[],
    keywords=["COOLBOOY-Multi-Provider AI Assistant"],
    entry_points={
        "console_scripts": [
            "COOLBOOY=COOLBOOY.cli.main:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    package_data={"": ["*.png", "*.jpg", "*.jpeg", "*.gif"]},
)
