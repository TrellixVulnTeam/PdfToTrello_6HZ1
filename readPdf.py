import pdfrw 
import os
import sys
import tempfile
import subprocess
"""
pass in pdf file
for every page in pdf
	run through every annotation
		
"""
"""
message = str(gPdfFile.pages[0].Annots[2].Contents)

print (message)

coords = str(gPdfFile.pages[0].Annots[2].Rect)

print (coords)

owner = str(gPdfFile.pages[0].Annots[2].T)

print (owner)

owner = str(gPdfFile.pages[0].CropBox)
"""


class PdfData:

	def __init__(self, pdfFile):
		self.m_Pages = []
		self.processPages(pdfFile)
	
	def processPages(self, pdfFile):
		for page in pdfFile.pages:
			print('process page')
			self.m_Pages.append(Page(page))			


class Page:
	def __init__(self, page):
		self.m_Comments = []
		self.m_PageWidth = 0
		self.m_PageHeight = 0
		#get all comment data
		numComments = len(page.Annots)
		currentIndex = 0
		self.m_PageWidth = int(float(page.CropBox[2]))
		self.m_PageHeight = int(float(page.CropBox[3]))
		while True:
			self.m_Comments.append(Comment(page.Annots[currentIndex], self))
			print('process comment')
			#we increase by two because pdf appears to store each annotation twice
			currentIndex += 2
			if currentIndex > numComments - 1:
				break


class Comment:
	'''
	m_CommentString = ''
	m_CommentLocationX = 0
	m_CommentLocationY = 0 
	m_CommentOwner = ''
	m_CommentRelativeLocationX = 0
	m_CommentRelativeLocationY = 0
	'''

	def __init__(self, annot, page):
		self.m_CommentString = annot.Contents
		self.m_CommentLocationX = int(float(annot.Rect[2]))
		self.m_CommentLocationY = int(float(annot.Rect[3]))
		self.m_CommentOwner = annot.T
		self.m_CommentRelativeLocationX = self.m_CommentLocationX / page.m_PageWidth
		self.m_CommentRelativeLocationY = self.m_CommentLocationY / page.m_PageHeight 
		print(self.m_CommentString)
		print('Relative Location X: ' + str(self.m_CommentRelativeLocationX))
		print('Relative Location Y: ' + str(self.m_CommentRelativeLocationY))


def annotatePages(_pdf):

	#for every page
	pageNum = 1
	for page in _pdf.m_Pages:
		#if the page has comments
		if page.m_Comments:
			#pull out the page image
			extractPageImage(pageNum, _pdf)
			
		pageNum += 1

def extractPageImage(pageNum, _pdf):
	#make the output directory if it doesn't already exist
	if not os.path.exists(gProgramDirectory + '\\tempworkingdir'):
		os.mkdir(gProgramDirectory + '\\tempworkingdir')
	#gswin32c -dNOPAUSE -dBATCH -sDEVICE=jpeg -dShowAnnots=false -dFirstPage=x -dLastPage=x -sOutputFile=x.xxx pdf.pdf
	exePath = gProgramDirectory + '\\gs9.21\\bin\\gswin32c.exe' 
	args = ' -dNOPAUSE -dBATCH -sDEVICE=jpeg -dShowAnnots=false '
	pageNumber = '-dFirstPage=' + str(pageNum) + ' -dLastPage=' + str(pageNum) + ' '
	outputFile = '-sOutputFile=' + gProgramDirectory + '\\tempworkingdir\\temppage_' + str(pageNum) + '.jpg '
	inputFile =  gInputPdfFile

	fullArgs = exePath + args + pageNumber + outputFile + inputFile
	runExternalProgramFromBatch(fullArgs)
	annotateImage(pageNum, _pdf)

def annotateImage(pageNum, _pdf):
	#resize page image
	exePath = 'imagemagick\\convert '
	pdfImage = gProgramDirectory + '\\tempworkingdir\\temppage_' + str(pageNum) + '.jpg ' 
	args = '-resize 1500x1500 '
	fullArgs = exePath + pdfImage + args + pdfImage
	runExternalProgramFromBatch(fullArgs)

	#for every comment
	#place annotation at relative location
	currentComment = 1
	while True:
		if currentComment > len(_pdf.m_Pages[pageNum - 1].m_Comments):
			break
		args = ' -background yellow -fill black -font impact -size 25x25 -gravity center label:' + str(currentComment) + ' tempworkingdir\\number.jpg'
		fullArgs = exePath + args
		runExternalProgramFromBatch(fullArgs)
		#imagemagick\convert.exe -background yellow -fill black -font impact -size 25x25 -gravity center label:number output.jpg
		#imagemagick\composite -gravity SouthWest number.jpg image.jpg image.jpg
		currentComment += 1

def runExternalProgramFromBatch(args):
	# Create temporary batch file to call ffmpeg
	tempBatFile = tempfile.NamedTemporaryFile(suffix='.bat', delete=False)
	tempBatFile.write(bytes(args, 'UTF-8'))
	tempBatFile.close()

	subprocess.call(tempBatFile.name)

	#remove temp batch file
	os.remove(tempBatFile.name)


gProgramDirectory = os.path.dirname(sys.argv[0])
gInputPdfFile = str(sys.argv[1])

#TODO pdf will be passed in dynamically
gPdfFile = pdfrw.PdfReader(gInputPdfFile)

#collect all annotation data inside the supplied pdf
gPdfData = PdfData(gPdfFile)
annotatePages(gPdfData)





