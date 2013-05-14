# log files
LATESTFILE = 'bot_latest.txt'
LOGFILE = 'bot_log.txt'

# config file
CONFIG = 'bot.cfg'

# import the modules we need to use
import twitter, os, time, sys
from random import choice
from config import Config

if os.path.exists(CONFIG):
    file = file(CONFIG)
    config = Config(file)

# connect to Twitter API
api = twitter.Api(consumer_key=config.consumer_key,
    consumer_secret=config.consumer_secret,
    access_token_key=config.access_token_key,
    access_token_secret=config.access_token_secret)

# grab the last ID that the bot replied to, so it doesn't reply to earlier posts. (spam prevention measure)
if os.path.exists(LATESTFILE):
    latest_file = open(LATESTFILE)
    last_id = latest_file.read().strip()
    latest_file.close()

    if last_id == '':
        last_id = 0
else:
    last_id = 0

# read in the file of users we've already responded to
log_file = open(LOGFILE)
already_messaged = log_file.readlines()
log_file.close()

# format the log file
for i in range(len(already_messaged)):
    if already_messaged[i].strip() == '':
        continue

    already_messaged[i] = already_messaged[i].replace('\n', '').split('|')[1].replace('\n', '')
already_messaged.append('CatCoding') # don't reply to myself

# perform the search
results = api.GetSearch('coding', 'hard', since_id=last_id)

# uncomment out the next line to test that you are getting results from your api search
# print 'Found %s results.' % (len(results))

# if no results, quit
if len(results) == 0:
    sys.exit()

# create a list of statuses you want to send
tweets = [
    "Hang in there! Coding iz funz! http://goo.gl/q1St8",
    "Coding luvs you! Hang in there! http://goo.gl/q1St8",
];

# create an array of users you've replied to
replied_to = []

# for each result within the results we got back from the Twitter API
for status in results:
    post_time = time.mktime(time.strptime(status.created_at[:-6], '%a, %d %b %Y %H:%M:%S'))

    # if the post happened after this script was run, and we haven't already messaged this user, and we're not replying to our self 
    if time.time() - (24*60*60) < post_time and status.user.screen_name not in already_messaged and '@bot' not in status.text.lower():
        if [True for x in already_messaged if ('@' + x).lower() in status.text.lower()]:
            continue

        try:
            api.PostUpdate('@%(screen_name)s %(tweet)s' % {'screen_name': status.user.screen_name, 'tweet': choice(tweets)}, in_reply_to_status_id=status.id)
            replied_to.append( (status.id, status.user.screen_name, status.text.encode('ascii', 'replace')) )
            time.sleep(1)
        except Exception:
            print "Unexpected error:", sys.exc_info()[0:2]

# write to our latest file
latest_file = open(LATESTFILE, 'w')
latest_file.write(str(max([x.id for x in results])))
latest_file.close()

# log the statuses we've replied to
log_file = open(LOGFILE, 'a')
log_file.write('\n'.join(['%s|%s|%s' % (x[0], x[1], x[2]) for x in replied_to]) + '\n')
log_file.write('\n')
log_file.close()
