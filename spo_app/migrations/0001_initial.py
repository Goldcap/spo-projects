# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MailingListSource'
        db.create_table(u'spo_app_mailinglistsource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('DateAdded', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 7, 0, 0), null=True, blank=True)),
        ))
        db.send_create_signal(u'spo_app', ['MailingListSource'])

        # Adding model 'VendorImage'
        db.create_table(u'spo_app_vendorimage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('ImgFile', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'spo_app', ['VendorImage'])

        # Adding model 'VendorProfile'
        db.create_table(u'spo_app_vendorprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('FirstName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('LastName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('Company', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('DateSubmitted', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 7, 0, 0), null=True, blank=True)),
            ('Address', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('Address1', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('City', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('State', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('Zip', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('Telephone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('BusinessTelephone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('Fax', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('Cell', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('Email', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('Website', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('Facebook', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('Twitter', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('Password', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('ShortDecs', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('Approved', self.gf('django.db.models.fields.IntegerField')(default=-1)),
        ))
        db.send_create_signal(u'spo_app', ['VendorProfile'])

        # Adding M2M table for field SelectedMailingLists on 'VendorProfile'
        m2m_table_name = db.shorten_name(u'spo_app_vendorprofile_SelectedMailingLists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vendorprofile', models.ForeignKey(orm[u'spo_app.vendorprofile'], null=False)),
            ('mailinglistsource', models.ForeignKey(orm[u'spo_app.mailinglistsource'], null=False))
        ))
        db.create_unique(m2m_table_name, ['vendorprofile_id', 'mailinglistsource_id'])

        # Adding M2M table for field SelectedImages on 'VendorProfile'
        m2m_table_name = db.shorten_name(u'spo_app_vendorprofile_SelectedImages')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vendorprofile', models.ForeignKey(orm[u'spo_app.vendorprofile'], null=False)),
            ('vendorimage', models.ForeignKey(orm[u'spo_app.vendorimage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['vendorprofile_id', 'vendorimage_id'])

        # Adding model 'FAQGroup'
        db.create_table(u'spo_app_faqgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal(u'spo_app', ['FAQGroup'])

        # Adding model 'FAQQuestion'
        db.create_table(u'spo_app_faqquestion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('Question', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('Answer', self.gf('django.db.models.fields.TextField')(default='', null=True, blank=True)),
            ('Group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['spo_app.FAQGroup'])),
            ('for_vendor', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'spo_app', ['FAQQuestion'])

        # Adding model 'MailingList'
        db.create_table(u'spo_app_mailinglist', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('FirstName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('LastName', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('EmailAddress', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('ZipCode', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('DateAdded', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2014, 2, 7, 0, 0), null=True, blank=True)),
        ))
        db.send_create_signal(u'spo_app', ['MailingList'])

        # Adding model 'ActivityLog'
        db.create_table(u'spo_app_activitylog', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('activity', self.gf('django.db.models.fields.CharField')(default='Login', max_length=20)),
            ('DateAdded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'spo_app', ['ActivityLog'])


    def backwards(self, orm):
        # Deleting model 'MailingListSource'
        db.delete_table(u'spo_app_mailinglistsource')

        # Deleting model 'VendorImage'
        db.delete_table(u'spo_app_vendorimage')

        # Deleting model 'VendorProfile'
        db.delete_table(u'spo_app_vendorprofile')

        # Removing M2M table for field SelectedMailingLists on 'VendorProfile'
        db.delete_table(db.shorten_name(u'spo_app_vendorprofile_SelectedMailingLists'))

        # Removing M2M table for field SelectedImages on 'VendorProfile'
        db.delete_table(db.shorten_name(u'spo_app_vendorprofile_SelectedImages'))

        # Deleting model 'FAQGroup'
        db.delete_table(u'spo_app_faqgroup')

        # Deleting model 'FAQQuestion'
        db.delete_table(u'spo_app_faqquestion')

        # Deleting model 'MailingList'
        db.delete_table(u'spo_app_mailinglist')

        # Deleting model 'ActivityLog'
        db.delete_table(u'spo_app_activitylog')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'spo_app.activitylog': {
            'DateAdded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'ActivityLog'},
            'activity': ('django.db.models.fields.CharField', [], {'default': "'Login'", 'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'spo_app.faqgroup': {
            'Meta': {'object_name': 'FAQGroup'},
            'Name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'spo_app.faqquestion': {
            'Answer': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'Group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['spo_app.FAQGroup']"}),
            'Meta': {'object_name': 'FAQQuestion'},
            'Question': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'for_vendor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'spo_app.mailinglist': {
            'DateAdded': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 7, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'EmailAddress': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'FirstName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'LastName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'Meta': {'object_name': 'MailingList'},
            'ZipCode': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'spo_app.mailinglistsource': {
            'DateAdded': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 7, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'Meta': {'object_name': 'MailingListSource'},
            'Name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'spo_app.vendorimage': {
            'ImgFile': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'Meta': {'object_name': 'VendorImage'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'spo_app.vendorprofile': {
            'Address': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Address1': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Approved': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'BusinessTelephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'Cell': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'City': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Company': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'DateSubmitted': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 2, 7, 0, 0)', 'null': 'True', 'blank': 'True'}),
            'Email': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Facebook': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'FirstName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'LastName': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'Meta': {'object_name': 'VendorProfile'},
            'Password': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'SelectedImages': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['spo_app.VendorImage']", 'symmetrical': 'False'}),
            'SelectedMailingLists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['spo_app.MailingListSource']", 'symmetrical': 'False'}),
            'ShortDecs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'State': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Telephone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'Twitter': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'Zip': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['spo_app']