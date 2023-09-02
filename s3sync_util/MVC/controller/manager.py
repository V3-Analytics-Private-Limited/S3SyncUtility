# controller.py
from model import *
from view import View

class Controller:
   """It controls both model and view files It takes the user input and it perform the user input related actions"""
   
   def upload(self):
       """This method redirect into model Files with upload actions"""
       model.upload.upload.upload_from_s3()
       pass
   
   def download(self):
       """This method redirect into model Files with download actions"""
       model.download.download_from_s3()
       pass
       
   def config(self):
       """This method redirect into model Files with cofig actions"""
       pass

view = View()
parser=view.create_parsers()
args = parser.parse_args()

control=Controller()

if args.command == 'upload':
    """It calss the upload method"""
    #Controller.upload()
    pass

elif args.command == 'download':
    """It calss the download method"""
    #Controller.download()
    pass

elif args.command == 'config':
    """IT calss the congig method"""
    #Controller.config()
    pass