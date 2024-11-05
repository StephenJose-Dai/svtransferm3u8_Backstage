# 介绍
基于我另一个项目svtransferm3u8开发的有后台管理的svtransferm3u8进阶版。

# 食用方法
```
mkdir -p /www
cd /www
git clone https://github.com/StephenJose-Dai/svtransferm3u8_Backstage.git m3u8
```
导入数据库
```
source /www/m3u8/db/m3u8info.sql
```
将m3u8.conf移动到nginx下
```
cd nginxconf
mv m3u8.conf /usr/local/nginx/conf/v_hosts
```
# 说明
1、mmsc.py是用来生成密码的，默认后台密码是123456，如果你觉得密码太简单，你可以用mmsc.py生成个加密密码，然后将生成的加密值复制粘贴到数据库的users表中的password字段  
2、app.py是后端，运行前需要将里面的配置和上传下载路径修改成你自己实际的  
3、请确保你安装了mysql8.x的数据库，我是基于centos stream 9部署的，所以你的mysql8.x要找el9的版本  
4、请确保你安装了nginx，如果是编译安装，一般我个人习惯是安装到/usr/local下，然后在/usr/local/nginx/conf下创建个v_hosts文件夹，将m3u8.conf移动到v_hosts里面，然后再到conf下把v_hosts下的m3u8.conf给引用到nginx.conf里面。  
   如果你是yum或者dnf安装的话，默认是在/etc/nginx下，我也会在conf下创建个v_hosts文件夹，将m3u8.conf移动到v_hosts里面，然后再到conf下把v_hosts下的m3u8.conf给引用到nginx.conf里面。  

# 支援
如果有部署问题或者其他问题，可以联系作者支援  

![戴戴的Linux](ddlnxqrcimg.jpg)
