FROM registry.aliyuncs.com/library/node:18-alpine AS builder

WORKDIR /app

# 使用国内镜像源
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

COPY package*.json ./
RUN npm install --registry=https://registry.npmmirror.com

COPY . .
RUN npm run build

FROM registry.aliyuncs.com/library/nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
