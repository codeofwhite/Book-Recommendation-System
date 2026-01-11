# mongo_custom_image/Dockerfile
FROM mongo:5.0.8 

# 在构建时生成 keyfile，并确保权限和拥有者正确
RUN mkdir -p /etc/mongo/ \
    && openssl rand -base64 128 | tr -d '\n' > /etc/mongo/mongodb_keyfile.txt \
    && chmod 600 /etc/mongo/mongodb_keyfile.txt \
    && chown mongodb:mongodb /etc/mongo/mongodb_keyfile.txt