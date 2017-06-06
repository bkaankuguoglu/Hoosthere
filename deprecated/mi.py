import BingSearchAPI as s

a = s.BingSpeechAPI()

def compareSentences( s1, s2):
	match = {}
	s1words = s1.lower().split(' ')
	s2words = s2.lower().split(' ')
	for w1 in s1words:
		for w2 in s2words:
			if w1 == w2:
				match[w1] = 1
				break

	return len(match)

print(compareSentences('be the change you wish to see in the world', a.recognize('sound_recog.wav')))

