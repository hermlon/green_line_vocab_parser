mkdir xml
for file in **.doc
	antiword -x db $file > xml/(basename -- "$file").xml
end
