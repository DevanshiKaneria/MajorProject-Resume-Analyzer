import os
from resume_parser import resumeparse

class ResumeParser:
    def __init__(self, resume):
        self.__resume = resume
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'degree': None,
            'no_of_pages': None,
        }
        self.__extract_details()

    def get_extracted_data(self):
        return self.__details

    def __extract_details(self):
        # If input is a file-like object, save temporarily
        if hasattr(self.__resume, 'read'):
            temp_path = "temp_resume.pdf"
            with open(temp_path, "wb") as f:
                f.write(self.__resume.read())
            file_path = temp_path
        else:
            file_path = self.__resume

        # Use resume-parser to extract data
        data = resumeparse.read_file(file_path)

        # Fill in the details dictionary
        self.__details['name'] = data.get('name')
        self.__details['email'] = data.get('email')
        self.__details['mobile_number'] = data.get('mobile_number')
        self.__details['skills'] = data.get('skills')
        self.__details['degree'] = data.get('degree')
        
        # Page count (optional, simple approximation)
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            self.__details['no_of_pages'] = len(reader.pages)
        except:
            self.__details['no_of_pages'] = None

        # Remove temp file if used
        if hasattr(self.__resume, 'read') and os.path.exists(temp_path):
            os.remove(temp_path)


# Optional wrapper for multiprocessing
def resume_result_wrapper(resume):
    parser = ResumeParser(resume)
    return parser.get_extracted_data()


if __name__ == '__main__':
    import pprint
    import multiprocessing as mp

    pool = mp.Pool(mp.cpu_count())
    resumes = []

    for root, directories, filenames in os.walk('resumes'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [pool.apply_async(resume_result_wrapper, args=(x,)) for x in resumes]
    results = [p.get() for p in results]
    pprint.pprint(results)
