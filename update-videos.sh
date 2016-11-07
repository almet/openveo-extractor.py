cd player
../venv/bin/python ../extractor.py ../list.json content
../venv/bin/python ../index_generator.py ../list.json
cd ..
rm -fr ../pyconfr-2016/videos
mv player ../pyconfr-2016/videos
git checkout player

