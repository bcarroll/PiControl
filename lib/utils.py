# coding=utf8
from OpenSSL import crypto, SSL
from socket import gethostname
from time import gmtime, mktime
from os.path import exists, join

def generate_ssl_cert(certfile='SSL/server.crt', keyfile='SSL/server.key', key_size=2048, cn=gethostname()):
	'''
	Generate a self-signed SSL certificate and key
	'''
	# create a key pair
	key = crypto.PKey()
	key.generate_key(crypto.TYPE_RSA, key_size)

	# create a self-signed cert
	cert = crypto.X509()
	cert.get_subject().CN = cn
	cert.set_serial_number(3141)
	cert.gmtime_adj_notBefore(0)
	cert.gmtime_adj_notAfter(10*365*24*60*60)
	cert.set_issuer(cert.get_subject())
	cert.set_pubkey(key)
	cert.sign(key, 'sha256')
	open(certfile, "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
	open(keyfile, "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
