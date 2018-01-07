# -*- coding: utf-8 -*-
#数据库文件，定义了数据操作的所有处理器
import tornado.ioloop
import tornado.web
import dbconn

dbconn.register_dsn("host=localhost dbname=studentMS user=admin01 password=pass")

class BaseReqHandler(tornado.web.RequestHandler):
    def db_cursor(self, autocommit=True):
        return dbconn.SimpleDataCursor(autocommit=autocommit)

#定位登录界面
class MainHandler(BaseReqHandler):
    def get(self):         
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.render("index.html", title="管理学院课程管理系统")

#检查登录用户是学生、教师、管理员
#如果登录用户是学生，定位到/student界面，登录用户是教师，定位到/teacher界面，登录用户是管理员，定位/admin界面              
class CheckHandler(BaseReqHandler):
    def post(self):        
        login_no = self.get_argument("login_no")
        if login_no[0]=='s':            
            self.redirect("/student")
        elif login_no[0]=='a':
            self.redirect("/admin")
        else:
            self.redirect("/teacher")
#学生界面处理器，展示学生课程的详细信息
class StudentHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
                sql='''SELECT student_sno,student_sname,student_sclass,teacher_tno,teacher_tname,
                sc_stime,sc_sday,sc_sweek,sc_splace 
                FROM student,course,teacher,sc,tc
                WHERE student_sno=sc_sno AND teacher_tno=sc_tno
                AND sc_cno=course_cno  AND sc_sno=tc_sno AND tc_sno=student_sno
                AND tc_tno=teacher_tno 
                ORDER BY student_sno'''
                cur.execute(sql)
                student_items = cur.fetchall()
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.render("student.html", title="学生课程信息", student_items=student_items)
#教师界面处理器，展示教师课程的详细信息
class TeacherHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
                sql = '''SELECT teacher_tno,teacher_tname,course_cno,course_cname,student_sno, student_sname,student_sclass, 
                tc_ttime,tc_tday,tc_tweek,tc_tplace 
                FROM student,course,teacher,tc
                WHERE  tc_sno=student_sno AND tc_tno=teacher_tno AND course_cno=tc_cno
                ORDER BY teacher_tno,student_sno'''
                cur.execute(sql)         
                teacher_items = cur.fetchall()
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.render("teacher.html", title="教师课程信息", teacher_items=teacher_items)
#管理员界面处理器，展示管理员的所有操作和信息，可以进行课程时间、地点的修改；课程的删除、修改
class AdminHandler(BaseReqHandler):
    def get(self):
        with self.db_cursor() as cur:
                sql = '''SELECT teacher_tno,teacher_tname,course_cno,course_cname,student_sno, student_sname,student_sclass, 
                tc_ttime,tc_tday,tc_tweek,tc_tplace 
                FROM student,course,teacher,tc
                WHERE  tc_sno=student_sno AND tc_tno=teacher_tno AND course_cno=tc_cno
                ORDER BY teacher_tno,student_sno'''
                cur.execute(sql)         
                teacher_items = cur.fetchall()
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.render("admin.html", title="教师课程信息", teacher_items=teacher_items)
        

#管理员使用的课程信息删除处理器
class CourseDelHandler(BaseReqHandler):
    def get(self, teacher_tno, course_cno):        
        with self.db_cursor() as cur:
            sql1 = '''
            DELETE FROM teacher 
                WHERE teacher_tno= %s '''
            cur.execute(sql1, (teacher_tno,))
            cur.commit()
            sql2 = '''
            DELETE FROM course
                WHERE course_cno= %s '''
            cur.execute(sql2, (course_cno,))
            cur.commit()

        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.redirect("/admin")
#管理员使用的课程信息修改处理器
class CourseEditHandler(BaseReqHandler):
    def get(self, tc_tno, tc_cno):       
        with self.db_cursor() as cur:
            sql = '''
            SELECT tc_ttime,tc_tday,tc_tweek,tc_tplace FROM tc
                WHERE tc_tno = %s AND tc_cno = %s;
            '''
            cur.execute(sql, (tc_tno, tc_cno))
            row = cur.fetchone()
            if row:
                self.render("courseEdit.html", tc_tno=tc_tno,tc_cno=tc_cno,tc_ttime=row[0],tc_tday=row[1], tc_tweek=row[2],
                    tc_tplace=row[3])
            else:
                self.write("没有查找到该条数据！")
        self.set_header("Content-Type", "text/html; charset=UTF-8")
    
    def post(self, tc_tno, tc_cno):       
        tc_ttime = self.get_argument("tc_ttime")
        tc_tday = self.get_argument("tc_tday")
        tc_tweek = self.get_argument("tc_tweek")
        tc_tplace = self.get_argument("tc_tplace")
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        with self.db_cursor() as cur:
            sql = '''
            UPDATE tc SET tc_ttime=%s,tc_tday=%s,tc_tweek=%s,tc_tplace=%s
                WHERE tc_tno= %s AND tc_cno= %s'''
            cur.execute(sql, (tc_ttime,tc_tday,tc_tweek,tc_tplace,tc_tno, tc_cno))
            cur.commit()
        self.set_header("Content-Type", "text/html; charset=UTF-8") 
        self.redirect("/admin")
#管理员使用的课程信息添加处理器
class CourseAddHandler(BaseReqHandler):                 
    def post(self):
        tc_tno = self.get_argument("tc_tno")
        student_sno = self.get_argument("student_sno")
        course_cno = self.get_argument("course_cno")
        tc_ttime = self.get_argument("tc_ttime")
        tc_tday = self.get_argument("tc_tday")
        tc_tweek = self.get_argument("tc_tweek")
        tc_tplace = self.get_argument("tc_tplace")
        
        with self.db_cursor() as cur:
            sql = '''INSERT INTO tc 
            (tc_tno, tc_sno, tc_cno,
            tc_ttime,tc_tday,tc_tweek,tc_tplace)  
            VALUES( %s, %s, %s,%s,%s,%s,%s);'''
            cur.execute(sql, (tc_tno, student_sno, course_cno,tc_ttime,tc_tday,tc_tweek,tc_tplace))
            cur.commit()
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.redirect("/admin")
    
        
        
application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/checkuser", CheckHandler),
    (r"/student",StudentHandler),
    (r"/teacher",TeacherHandler),
    (r"/admin",AdminHandler),
    (r"/courseDel/([a-z0-9]+)/([0-9]+)",CourseDelHandler),
    (r"/courseEdit/([a-z0-9]+)/([0-9]+)",CourseEditHandler),
    (r"/courseAdd",CourseAddHandler)    
], debug=True)

if __name__ == "__main__":
    application.listen(8888)
    server = tornado.ioloop.IOLoop.instance()
    tornado.ioloop.PeriodicCallback(lambda: None, 500, server).start()
    server.start()

