from skbuild import setup
setup(
    name="simple-language-recognizer",
    version="0.0.3",
    cmake_install_dir=".",
    #cmake_args=["-DCMAKE_GENERATOR_PLATFORM=x64"],
    #platforms=["win_amd64"],
    #py_modules=["simpleLanguageRecognizer"]
)