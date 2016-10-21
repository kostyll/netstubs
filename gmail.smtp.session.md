1)EHLO localhost

# perl -MMIME::Base64 -e 'print encode_base64("\000kostyll\@gmail.com\000$(cat gmail.pass)")' 
# python -c 'import base64;print base64.b64encode("\0%s@gmail.com\0%s" % ("kostyll", open("gmail.pass").read()))'

#http://stackoverflow.com/questions/11046135/how-to-send-email-using-simple-smtp-commands-via-gmail

2)AUTH PLAIN ^^^^^

