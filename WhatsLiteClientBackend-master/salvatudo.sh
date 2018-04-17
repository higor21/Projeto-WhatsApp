echo "Digite o texto da commit"
read textcommit
git add *
git commit -m "$textcommit"
git push origin master