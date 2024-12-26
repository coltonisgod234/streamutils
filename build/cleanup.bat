:: Delete build

cd build
del *.* /S
cd ..
rmdir build

:: Delete dist

cd dist
del *.* /S
cd ..
rmdir dist

:: Delete spec

del ttsfront.spec
pause