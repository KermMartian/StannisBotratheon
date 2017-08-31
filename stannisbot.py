#!/usr/bin/python
# --------------------------------------------------------------------
# StannisBotratheon: Grammar King of Westeros
# Author: Christopher Mitchell, Ph.D.
# 
# Stannis Botratheon does what Stannis Baratheon, First of His Name,
# would do: he corrects misuse of the word "less" to "fewer" in
# Reddit posts using the Spacy grammar engine.
# --------------------------------------------------------------------
import praw
import re
import spacy

# Reddit Setup (remember to create praw.ini!)
botname = "Stannisbot"
username = "StannisBotratheon"
subreddit = "gameofthrones"

# Reply template and file to track replied post IDs
reply_template = "> {}\n\n[Fewer.](https://i.imgur.com/30JMpQe.jpg)\n\n" + \
                 "*I am Stannis Botratheon, First of His Name. If I misbehave, please notify u/KermMartian.*";
replied_file = "replied.txt"

nlp = spacy.load("en")
less_re = re.compile(r"(^|\s)([Ll][Ee][Ss][Ss] [A-Za-z]+)")

class FewerFactory:
	def __init__(self, replied_path):
		self.replied = {}
		try:
			with open(replied_path, 'r') as f:
				for line in f.readlines():
					self.replied[line.strip()] = True
		except IOError:
			pass
		self.replied_fp = open(replied_path, 'a')
		
	def fewerReply(self, comment):
		# See if we already replied
		do_reply = True
		if comment.fullname in self.replied:
			do_reply = False
			return

		if comment.author.name == botname or comment.author.name == username:
			return

		for reply in comment.replies:
			if reply.author.name == botname or reply.author.name == username:
				return

		try:
			matches = re.findall(less_re, comment.body.encode('utf8'))
			for match in matches:
				input_phrase = match[1].strip()
				print "%s processing %s" % (botname, input_phrase)
				document = nlp(input_phrase.decode('utf8'))
				print "%s: %s" % (input_phrase, document[1].tag_)
				if "NNS" == document[1].tag_:
					print "%s: Replying to %s" % (botname, comment.fullname)
					reply_text = reply_template.format(input_phrase)
					comment.reply(reply_text)
					self.replied[comment.fullname] = True
					self.replied_fp.write("%s\n" % (comment.fullname))
	
		except UnicodeEncodeError:
			print("Unicode failure; continuing")
			pass
	
def main():

	reddit = praw.Reddit(botname)
	subreddit = reddit.subreddit(subreddit)
	fewer_factory = FewerFactory(replied_file)
	
	for comment in subreddit.stream.comments():
		if "less " in comment.body.lower():
			fewer_factory.fewerReply(comment)

if __name__ == "__main__":
	main()
