from django.db import models
from werkzeug.security import generate_password_hash, check_password_hash
from pysnmp.entity.rfc3413.oneliner import cmdgen
import datetime
import sys

# Create your models here.

class User(models.Model):

    #id = db.Column(db.Integer, primary_key=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.CharField(max_length=120,unique=True)
    #password = db.Column(db.String(100))
    pwdhash = models.CharField(max_length=254)
    role = models.IntegerField()

    #posts = db.relationship('Post',backref='author',lazy = 'dynamic')

    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)

    def is_authenticated(self):
        return True

    def get_id(id):
        for user in User:
            if user[0] == id:
                return user(user[0], [1])
        return None

    def __str__(self):
        return '<User %r>' % (self.email)

class Node(models.Model):

    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.

    ip_address = models.CharField(max_length=30,null=False)
    community = models.CharField(max_length=20)
    hostname = models.CharField(max_length=50)
    interfaces = models.ForeignKey(Interface)
    def to_json(self):
        return dict(id = self.id, ip_address=self.ip_address, community = self.community, hostname=self.hostname)


class Interface(models.Model):

    ifName = models.CharField(max_length=50)#.Column(db.String(50))
    ifAlias = models.CharField(max_length=200)#Column(db.String(200))
    ifIndex = models.IntegerField()#db.Column(db.Integer)
    ifSpeed = models.BigIntegerField()#db.Column(db.BigInteger)
    ifOperStatus = models.IntegerField()#db.Column(db.Integer)
    last_in_octet_read = models.BigIntegerField()#db.Column(db.BigInteger)
    this_in_octet_read = models.BigIntegerField()#db.Column(db.BigInteger)
    last_out_octet_read = models.BigIntegerField()#db.Column(db.BigInteger)
    this_out_octet_read = models.BigIntegerField()#db.Column(db.BigInteger)


    #node = db.relationship(Node)
    #octets = db.relationship('InterfaceOctets', lazy='dynamic')

    def __str__(self):
        return "<Interface('node_id='%s', ifName='%s', ifAlias='%s', ifIndex='%d')>" % \
               (self.node_id, self.ifName, self.ifAlias, self.ifIndex.value_to_string())

    def get_octets2(self, view_time_in_hours=24):
        temp_diff = datetime.datetime.now() - datetime.timedelta(hours=view_time_in_hours)
        data = self.octets.filter(InterfaceOctets.collected_at > temp_diff)\
            .order_by(InterfaceOctets.collected_at).all()
        this_in = 0
        last_in = 0
        this_out = 0
        last_out = 0

        return_data = []

        first_time = True
        for entry in data:

            # print entry.collected_at, interface.id
            this_time = entry.collected_at
            if this_in != 0:
                last_in = this_in

            this_in = entry.ifInOctets

            if last_in != 0:
                time_diff = this_time - last_time
                # print time_diff.seconds
                num_octets = 0
                if last_in > this_in:
                    num_octets = sys.maxsize - last_in + this_in
                else:
                    num_octets = this_in - last_in

                rate_in = ((num_octets)/time_diff.seconds)*8

            else:
                rate_in = 0

            if this_out != 0:
                last_out = this_out

            this_out = entry.ifOutOctets
            if last_out != 0:
                num_octets = 0
                if last_out > this_out:
                    num_octets = sys.maxsize - last_out + this_out
                else:
                    num_octets = this_out - last_out
                rate_out = ((num_octets)/time_diff.seconds)*8

            else:
                rate_out = 0

            instance = {'date':str(this_time), 'input_rate':rate_in, 'output_rate':rate_out}

            return_data.append(instance)

            last_time = this_time

        return return_data
    def get_octets(self, view_time_in_hours=24):
        temp_diff = datetime.datetime.now() - datetime.timedelta(hours=view_time_in_hours)
        data = self.octets.filter(InterfaceOctets.collected_at > temp_diff)\
            .order_by(InterfaceOctets.collected_at).all()

        return_data = []

        data_len = len(data)
        for index in range(0,data_len - 1):
            this_entry = data[index]
            next_entry = data[index+1]

            time_diff = next_entry.collected_at - this_entry.collected_at
            if next_entry.ifInOctets > this_entry.ifInOctets:
                in_octets = next_entry.ifInOctets - this_entry.ifInOctets
            else:
                in_octets = sys.maxsize - next_entry.ifInOctets + this_entry.ifInOctets
            if next_entry.ifOutOctets > this_entry.ifOutOctets:
                out_octets = next_entry.ifOutOctets - this_entry.ifOutOctets
            else:
                out_octets = sys.maxsize - next_entry.ifOutOctets + this_entry.ifOutOctets

            rate_in = ((in_octets)/time_diff.seconds)*8
            rate_out = ((out_octets)/time_diff.seconds)*8

            instance = {'date':str(next_entry.collected_at), 'input_rate':rate_in, 'output_rate':rate_out}

            return_data.append(instance)

        return return_data

    def get_stats(self,hours=24):
        print('getting stats for interface %s'%self.id)
        try:
            data = self.get_octets(int(hours))
            #print (id, data)
            avg_in_data = []
            avg_out_data = []
            collected_at = []
            total_in = 0
            total_out = 0
            max_in = 0
            max_out = 0
            ifInOctets = []
            ifOutOctets = []
            for entry in data:
                date = entry['date']
                rate_in = entry['input_rate']
                rate_out = entry['output_rate']
                total_in += ((int(rate_in)*5*60)/8)
                total_out += ((int(rate_out)*5*60)/8)
                avg_in_data.append(rate_in)
                avg_out_data.append(rate_out)
                if rate_in > max_in:
                    max_in = rate_in
                if rate_out > max_out:
                    max_out = rate_out

                ifInOctets.append(rate_in)
                ifOutOctets.append(rate_out)
                collected_at.append(date)

            avg_in = sum(avg_in_data)/len(avg_in_data)
            avg_out = sum(avg_out_data)/len(avg_out_data)
            #print avg_in, avg_out
            nine_out_array = sorted(ifOutOctets)
            nine_in_array = sorted(ifInOctets)
            #print nine_in_array
            #print ifInOctets
            nine_in_len = len(nine_in_array)
            nine_out_len = len(nine_out_array)
            nine_out_percentile = nine_out_array[int(nine_out_len*.95)]
            nine_in_percentile = nine_in_array[int(nine_in_len*.95)]
            print('interface %s stats complete'%self.ifName)
            response = {"nine_in":nine_in_percentile, "nine_out":nine_out_percentile, "avg_in":avg_in,
                        "avg_out":avg_out, "total_in":total_in, "total_out":total_out}
        except:
            response = {"nine_in":0, "nine_out":0, "avg_in":0, "avg_out":0, "total_in":0, "total_out":0}

        return response


class InterfaceOctets(models.Model):

    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    #id = db.Column(db.Integer, primary_key=True, index=True)
    ifInOctets = models.BigIntegerField()#db.Column(db.BigInteger)
    ifOutOctets = models.BigIntegerField()#db.Column(db.BigInteger)
    collected_at = models.DateTimeField(default=datetime.datetime.now())#db.Column(db.DateTime, default = datetime.datetime.now())
    interface = models.ForeignKey(Interface)
    #interface_id = db.Column(db.Integer, db.ForeignKey('interface.id'), index=True)
    #interface = db.relationship(Interface)


