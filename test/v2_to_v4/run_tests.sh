cd Ne22_v2
rm *.wav
rm log_*
rm summary_*
bash Ne22_usda.sh
cd ..
cd Ne22_v4
rm *.wav
rm log_*
rm summary_*
bash Ne22_usda.sh
cd ..
cd V50_v2
rm *.wav
rm log_*
rm summary_*
bash V50_gxpf1a.sh
cd ..
cd V50_v4
rm *.wav
rm log_*
rm summary_*
bash V50_gxpf1a.sh
cd ..
python compare.py