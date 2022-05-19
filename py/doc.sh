cd ~/app/uxf/py
pydoc -w uxf > /dev/null
rm -f ~/qtrac/www-live/static/uxf-api.html
mv uxf.html ~/qtrac/www-live/static/uxf-api.html
echo wrote ~/qtrac/www-live/static/uxf-api.html
cd ..
