res = ""
for i in range(0, 40):
    res += "echo \"test" + str(i) + "\"\nTYPE test" + str(i) + ".txt\n..\\res\DLanguage.exe test" + str(i) + ".txt > test" + str(i) + ".cs\ncsc test" + str(i) + ".cs\ntest" + str(i) + ".exe\npause\ncls\n\n\n"
print(res)