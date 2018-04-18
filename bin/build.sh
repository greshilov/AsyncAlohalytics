mkdir -p temp
cd temp && \
   cmake ../c++ && \
   make && \
   mv pyalohareciever.so ../server/pyalohareciever.so

cd ../ && \
   rm -rf temp
