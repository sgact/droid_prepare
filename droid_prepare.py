import argparse
import os
import re


def logi(msg):
    print msg

def parseArgument():
    parser = argparse.ArgumentParser(description='Make an Android Project Fits Your Computer', epilog='Use the -h for help')
    parser.add_argument("path", help='path to project')
    return parser.parse_args()

class Main:

    def __init__(self, args):
        self.args = args
        self.gradle_version = ''
        self.sdk_version = ''
        self.now_best_cp_version = '3.1.4'

    def prepare_git(self):
        if self.args.path.endswith('.git'):
            os.system('git clone ' + self.args.path)
            repo_name = self.args.path.split('/')[-1][:-4]
            self.args.path = os.path.join(os.getcwd(), repo_name)


    def get_version_num(self, version_name):
        version_num = 0
        for i, each in enumerate(reversed(version_name.split('.'))):
            version_num += 10**i + eval(each)
        return version_num

    def get_local_env(self):
        #get gradle
        gradle_dir = '%s/.gradle/wrapper/dists' % (os.path.expanduser('~'))
        gradle_dist_pat = re.compile('gradle-(\d*\.\d*(?:\.\d*)?)-all')
        logi(os.listdir(gradle_dir))
        max_gradle_version = 0
        for each in os.listdir(gradle_dir):
            version = gradle_dist_pat.findall(each)
            if version and self.get_version_num(version[0]) > max_gradle_version:
                max_gradle_version = version
        logi(max_gradle_version)
        self.gradle_version = max_gradle_version[0]
        #get android sdk
        #I think you must put sdk in your path
        android_sdk = os.path.dirname(os.path.dirname(os.popen('which adb').read())) + '/platforms'
        logi(android_sdk)
        android_pat = re.compile('android-(\d\d)')
        max_sdk_version = 0
        for each in os.listdir(android_sdk):
            version = android_pat.findall(each)
            logi(version)
            if version and max_sdk_version < eval(version[0]):
                max_sdk_version = eval(version[0])
        logi(max_sdk_version)
        self.sdk_version = str(max_sdk_version)

    def replace_file(self, path, pat, text):
        with open(path, 'rw') as file:
            file_line_copy = file.readlines()
            for i, each_line in enumerate(file_line_copy):
                re_result = pat.findall(each_line)
                if re_result:
                    line = each_line.replace(re_result[0], text)
                    file_line_copy[i] = line
        os.remove(path)
        with open(path, 'w') as file:
            file.writelines(file_line_copy)

    def add_google_mvn(self, path):
        '''repositories {
                jcenter()
                google()
            }'''
        with open(path, 'r') as file:
            file_txt = file.read()
            google_pat = re.compile('[.\n]*repositories[^\}]*}')
            find_result = google_pat.findall(file_txt)
            if find_result and 'google' not in find_result[0]:
                each_copy = find_result[0]
                each_copy = each_copy.replace('\n', '\n        google()\n', 1)
                file_txt = file_txt.replace(find_result[0], each_copy, 1)

        os.remove(path)
        with open(path, 'w') as file:
            file.write(file_txt)

    def rewrite_verison(self):
        for root, _, files in os.walk(self.args.path):
            for file in files:
                if file == 'build.gradle':
                    path = os.path.join(root, file)
                    pat1 = re.compile('\s?classpath \'com.android.tools.build:gradle:(.*)\'')
                    pat2 = re.compile('\s?compileSdkVersion (.*)')
                    pat3 = re.compile('\s?targetSdkVersion (.*)')
                    self.replace_file(path, pat1, self.now_best_cp_version)
                    self.replace_file(path, pat2, self.sdk_version)
                    self.replace_file(path, pat3, self.sdk_version)
                    self.add_google_mvn(path)
                if file == 'gradle-wrapper.properties':
                    path = os.path.join(root, file)
                    pat = re.compile('distributionUrl=(?:.*)gradle-(.*)-all.zip')
                    self.replace_file(path, pat, self.gradle_version)

    def work(self):
        self.prepare_git()
        self.get_local_env()
        self.rewrite_verison()



if __name__ == '__main__':
    main = Main(parseArgument())
    main.prepare_git()
    main.work()
    print "done!"