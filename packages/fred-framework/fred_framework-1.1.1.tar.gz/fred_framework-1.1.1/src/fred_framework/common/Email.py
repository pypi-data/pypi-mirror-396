"""
 * @Author：cyg
 * @Package：email
 * @Project：Default (Template) Project
 * @name：email
 * @Date：2024/10/22 14:32
 * @Filename：email
"""
from fred_framework.common.Extensions import Extensions


class Email:
	
	def send_mail(self, mail_address, title, content):
		from flask_mail import Message
		msg = Message(title, recipients=[mail_address])
		msg.body = content
		msg.html = '<b>' + content + '</b>'
		try:
			Extensions().mail.send(msg)
			return 'Email sent!'
		except Exception as e:
			raise Exception(f'Error sending email: {str(e)}')
