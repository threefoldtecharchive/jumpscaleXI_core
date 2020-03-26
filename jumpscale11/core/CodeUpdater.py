method_replace = """
writeFile : file_write
readFile : file_read
j.sal.fs.writeFile : j.core.tools.file_write
j.sal.fs.readFile : j.core.tools.file_read
formatMessage : format_message
echoListItem : print_list_item
echoWithPrefix : print_with_prefix
echoListWithPrefix: print_with_prefix_list
echoDict : print_dict
transformDictToMessage
askString
askPassword
askInteger
askYesNo
askIntegers
askChoice
askChoiceMultiple : ask_choice_multiple
ask_choices : ask_choice
askMultiline
askArrayRow : ask_array_row
getOutput : output_get
hideOutput : output_hide
printOutput : output_print
enableOutput : output_enable
showArray : print_array
getMacroCandidates : macro_candidates_get
parseArgs : parse_pythoncode_arguments
parseDefLine : parse_pythoncode_method
pythonObjToStr1line : transform_pythonobject_1line
pythonObjToStr : transform_pythonobject_multiline
replaceQuotes : transform_quotes
j.core.tools.text_strip : j.data.text.strip
j.core.tools._check_interactive : j.tools.console.check_interactive
j.core.tools._j.core.myenv : j.core.myenv
j.core.tools.text_replace : j.data.text.replace
j.core.tools.text_strip : j.data.text.strip
j.core.tools.text_wrap : j.data.text.wrap
j.core.tools.text_replace : j.data.text.replace
j.core.tools.text_strip : j.data.text.strip
j.core.tools.text_wrap : j.data.text.wrap
j.core.tools.args_replace
j.core.tools._j.core.myenv.MYCOLORS
j.core.tools.text_strip_to_ascii_dense : j.data.text.strip_to_ascii_dense


"""

replace = """

"""

# means there needs to be a . behind
obj_part_replace = """
Tools.exceptions : j.exceptions
Tools : j.core.tools
j.core.tools._j : j
"""
