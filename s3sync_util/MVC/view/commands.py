# view.py
import argparse

class View:
  """This class defines the Argparse commands and itentify the user input then it redirect to the controller """
 
  parser = argparse.ArgumentParser(description="Upload and download directories/files from Amazon S3") 

  parser.add_argument('--version', action='version', version=f'S3Sync Utility v')
  subparsers = parser.add_subparsers(title='subcommands', dest='subcommand', description="Available subcommands for managing S3Sync:")
  
  def create_parsers(self):
    """Main entry point for the S3Sync utility."""
    """Inside this method it create the config, upload and download parsers and returns the args"""
    pass
  