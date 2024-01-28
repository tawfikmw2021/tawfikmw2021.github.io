cp -r ../CarteRami/rami-vue/dist rami-vue-dist  
cp ../CarteRami/rami-vue/server.py rami-vue-dist 
sed -r -i "s/\"\/js\//\"\/rami-vue-dist\/js\//g" rami-vue-dist/index.html
sed -r -i "s/\"img\//\"rami-vue-dist\/img\//g" rami-vue-dist/js/*
sed -r -i "s/\"\/css\//\"\/rami-vue-dist\/css\//g" rami-vue-dist/index.html