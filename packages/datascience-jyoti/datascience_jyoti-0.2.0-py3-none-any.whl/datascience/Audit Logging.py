import sys
import os
import logging
import uuid
import shutil
import time

# Determine base path
if sys.platform == 'linux':
    Base = os.path.expanduser('~') + '/VKHCG'
else:
    Base = 'C:/Users/JYOTI RAHATE/Downloads/DataScience'

# Companies, layers, logging levels
sCompanies = ['01-Vermeulen', '02-Krennwallner', '03-Hillman', '04-Clark']
sLayers = ['01-Retrieve', '02-Assess', '03-Process', '04-Transform', '05-Organise', '06-Report']
sLevels = ['debug', 'info', 'warning', 'error']

# Loop through companies and layers
for sCompany in sCompanies:
    sCompanyDir = os.path.join(Base, sCompany)
    if not os.path.exists(sCompanyDir):
        os.makedirs(sCompanyDir)

    for sLayer in sLayers:
        # Remove previous logging handlers
        log = logging.getLogger()
        for hdlr in log.handlers[:]:
            log.removeHandler(hdlr)

        # Setup logging directory
        sLogDir = os.path.join(Base, sCompany, sLayer, 'Logging')
        if os.path.exists(sLogDir):
            shutil.rmtree(sLogDir)
            time.sleep(1)  # give time for cleanup
        if not os.path.exists(sLogDir):
            os.makedirs(sLogDir)

        # Create unique log file
        skey = str(uuid.uuid4())
        sLogFile = os.path.join(sLogDir, f'Logging_{skey}.log')
        print('Set up:', sLogFile)

        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M',
            filename=sLogFile,
            filemode='w'
        )

        # Add console output
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        logging.info('Practical Data Science is fun!.')

        # Log messages for each level
        for sLevel in sLevels:
            sApp = f'Application-{sCompany}-{sLayer}-{sLevel}'
            logger = logging.getLogger(sApp)

            if sLevel == 'debug':
                logger.debug('Practical Data Science logged a debugging message.')
            elif sLevel == 'info':
                logger.info('Practical Data Science logged information message.')
            elif sLevel == 'warning':
                logger.warning('Practical Data Science logged a warning message.')
            elif sLevel == 'error':
                logger.error('Practical Data Science logged an error message.')
