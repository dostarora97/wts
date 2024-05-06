/usr/local/bin/platypus --app-icon '/Applications/Platypus.app/Contents/Resources/PlatypusDefault.icns'  --name 'WTS-Executable'  --interface-type 'Text Window'  --interpreter '/bin/sh'  --author 'DA25'   --bundle-identifier org.DA25.WTS-Executable --bundled-file "./dist/${executable_name}"  './bin/platypus-script.sh' './dist/WTS-Executable'

echo "App created in ./dist/WTS-Executable"
