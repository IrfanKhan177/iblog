# import markdown

# from decouple import config
import mysql.connector
import os
import datetime
from flask import Flask , render_template,abort, request,session, redirect, url_for
from markupsafe import escape
from werkzeug.utils import secure_filename
# import urllib.request
# import markdown.extensions.fenced_code
# from markupsafe import escape
app = Flask(__name__)
mydb = mysql.connector.connect(
  host=os.getenv('HOSTS'),
#   port=3306,
  user=os.getenv('USERS'),
  password=os.getenv('PASSW'),
  database=os.getenv('DATABASES')
)
print(mydb)
app.config['UPLOADED_PATH']="D:\\Blog Project"
app.secret_key=os.getenv('SECRET_KEY')
#INSERT INTO `posts` (`sno`, `slug`, `title`, `content`) VALUES (NULL, 'hello-g', 'Hello', 'hfghfgh');
mycursor = mydb.cursor()
pwd={"userw":f"{os.getenv('PASS')}","passw":f"{os.getenv('PASS')}"}

@app.route("/")
def index():
    sql = f"SELECT * FROM `posts` ORDER BY `sno` DESC LIMIT 8"
    mycursor.execute(sql)
    post = mycursor.fetchall()
    # print(post)
    
    return render_template("index.html",post=post)
@app.route("/blogs")
def blogs():
    sql = f"SELECT * FROM `posts` ORDER BY `sno` DESC"
    mycursor.execute(sql)
    post = mycursor.fetchall()
    # print(post)
    
    return render_template("blog.html",post=post)


@app.route("/blog/<slug>")
def blog(slug):
    try:
        sql = f"SELECT * FROM `posts` WHERE `slug` = '{slug}' "
        mycursor.execute(sql)
        post = mycursor.fetchall()
        # print(post)
        # title=post[0][2]
        # content=post[0][3]
        # desc= post[0][4]
        for it in post:
            print(it[5])
            return render_template("post.html",title=it[2],content=it[3],desc=it[4],time=it[5]),200
    except:
        abort(404)

@app.route('/search/', methods=['GET'])
def search():
    
    qTerm = request.args.get('s')
    sr= escape(qTerm)
    sql = f"SELECT * FROM `posts` WHERE `title` LIKE '%{sr}%' "
    
    mycursor.execute(sql)
    post = mycursor.fetchall()
    l= len(post)
    
    return render_template("search.html",post=post,length=l ,sr=sr)
@app.route("/admin",methods=['GET','POST'])
def admin():

    if ('user' in session and session['user']==pwd['userw']):
            sql = f"SELECT * FROM `posts` ORDER BY `sno` DESC"
            mycursor.execute(sql)
            post = mycursor.fetchall()
            # print(post)
            return render_template("admin.html",post=post)
        
            


    if request.method == 'POST':
        uname=request.form.get('user')
        upass=request.form.get('pass')
        if (uname==pwd['userw'] and upass==pwd['passw']):
            session['user']=uname
            sql = f"SELECT * FROM `posts`"
            mycursor.execute(sql)
            post = mycursor.fetchall()
            # print(post)
            return render_template("admin.html",post=post)
            
            

    
    return render_template("login.html",pwd=pwd)

@app.route('/create-post',methods=['GET','POST'])
def create_post():
     if ('user' in session and session['user']==pwd['userw']):
        if request.method =='POST':
            dtime=str(datetime.datetime.now())
            dtime=dtime.replace('.','_')
            dtime=dtime.replace(':','_')
            dtime=dtime.replace(' ','_')
            file = request.files['cover']
            filenames = dtime+secure_filename(file.filename)
            
            file.save(os.path.join(os.getcwd()+"\\static\\uploads",filenames))
            print(filenames)
            title = request.form.get('title')
            desc = request.form.get('description')
            slug = request.form.get('slug')
            content= request.form.get('content')
            sql = f"INSERT INTO `posts` (`sno`, `slug`, `title`, `content`, `desc`, `date`,`cover`) VALUES (NULL, '{slug}', '{title}', '{content}', '{desc}', current_timestamp(),'{filenames}')"

            mycursor.execute(sql)
            mydb.commit()

        return render_template('crpost.html',pwd=pwd)
     return redirect(url_for('admin'))

@app.route('/logout',methods=['GET','POST'])
def logout():
    if request.method == 'POST':
        lr= request.form.get('logout')
        if lr=='Logout':
            session.pop('user',None)
            return redirect(url_for('admin'))

@app.route('/edit/<sno>')
def edit(sno):
    if ('user' in session and session['user']==pwd['userw']):
        try:
            sql1 = "SELECT * FROM `photos`"
            mycursor.execute(sql1)
            posts = mycursor.fetchall()
            sql = f"SELECT * FROM `posts` WHERE `sno` = '{sno}' "
            mycursor.execute(sql)
            post = mycursor.fetchall()
            print(post)
            # title=post[0][2]
            # content=post[0][3]
            # desc= post[0][4]
            for it in post:
 
                # print(it[5])
                
                return render_template("edit.html",sno=it[0],slug=it[1],title=it[2],content=it[3],desc=it[4],time=it[5],file=it[6],post=posts),200
        except:
            abort(404)
    return redirect(url_for('admin'))
        

@app.route("/update",methods=['GET','POST'])
def update():
    if ('user' in session and session['user']==pwd['userw']):
        if request.method =='POST': 
            file = request.files['cover']
            if file:
                sn= request.form.get('serial')
                sql2=f"SELECT * FROM `posts` WHERE `sno` = {sn} "
                
                mycursor.execute(sql2)
                rem= mycursor.fetchall()
                print(rem)
                for i in rem:
                    if os.path.exists("static/uploads/"+i[6]):
                          os.remove("static/uploads/"+i[6])
                dtime=str(datetime.datetime.now())
                dtime=dtime.replace('.','_')
                dtime=dtime.replace(':','_')
                dtime=dtime.replace(' ','_')
          
                filenames = dtime+secure_filename(file.filename)
            
                file.save(os.path.join(os.getcwd()+"\\static\\uploads",filenames))
                sql=f"UPDATE `posts` SET `cover`='{filenames}' WHERE `posts`.`sno`={sn}"
                mycursor.execute(sql)
                mydb.commit()

            sn= request.form.get('serial')     
            title = request.form.get('title')
            descr = request.form.get('description')
            slug = request.form.get('slug')
            content= request.form.get('content')
            
            print(sn)
            sql = f"UPDATE `posts` SET `slug`='{slug}',`title`='{title}',`desc`='{descr}',`content`='{content}' WHERE `posts`.`sno`={sn}"
            # val=(slug,title,descr,content,sn)
            mycursor.execute(sql)
            mydb.commit()
            return redirect(url_for('admin'))
    return redirect(url_for('admin'))
@app.route('/delete/<sno>')
def delete(sno):
    if ('user' in session and session['user']==pwd['userw']):
        sql=f"DELETE FROM posts WHERE `posts`.`sno` = {sno}"
        mycursor.execute(sql)
        mydb.commit()
        return redirect(url_for('admin'))
    return redirect(url_for('admin'))

@app.route('/uploader', methods=['POST','GET'])
def imguploader():
    if ('user' in session and session['user']==pwd['userw']):
        if request.method == 'POST':
            
            
            dtime=str(datetime.datetime.now())
            dtime=dtime.replace('.','_')
            dtime=dtime.replace(':','_')
            dtime=dtime.replace(' ','_')
            file = request.files['photos']
            filenames = dtime+secure_filename(file.filename)
            
            file.save(os.path.join(os.getcwd()+"\\static\\photos",filenames))
            print(filenames)
            sql=f"INSERT INTO `photos` (`id`,`image`) VALUES (NULL,'{filenames}')"
            mycursor.execute(sql)
            mydb.commit()
            sql="SELECT * FROM `photos` ORDER BY `id` DESC"
            mycursor.execute(sql)
            
            imgs = mycursor.fetchall()
            print(imgs)
            
            return redirect('/uploader')
        sql="SELECT * FROM `photos`"
        mycursor.execute(sql)
            
        imgs = mycursor.fetchall()
        return render_template('imgs.html',ml=imgs)

    sql="SELECT * FROM `photos`"
    mycursor.execute(sql)
            
    imgs = mycursor.fetchall()
    print(imgs)
    return render_template("imgs.html",ml=imgs)

@app.route('/imgdel/<id>',methods=['POST','GET'])
def imgdel(id):
    
    if ('user' in session and session['user']==pwd['userw']):
        sql2=f"SELECT * FROM `photos` WHERE `id` = '{id}' "
        mycursor.execute(sql2)
        rem= mycursor.fetchall()
        for i in rem:
              os.remove("static/photos/"+i[1])
        sql=f"DELETE FROM photos WHERE `photos`.`id` = {id}"
        mycursor.execute(sql)
        mydb.commit()
        
        
            
        return redirect('/uploader')
    return redirect(url_for('admin'))

    


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404
# if __name__ == "__main__":
#     app.run(debug=True)