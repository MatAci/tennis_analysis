For Windows users:

	#Create a virtual environment  
	python3 -m venv env

	#Activate the virtual environment  
	env\Scripts\activate

	#Install the required packages  
	pip install -r requirements.txt

 For Linux users:

	# Create a virtual environment  
	python3 -m venv env

	# Activate the virtual environment  
	source env/bin/activate

	# Install the required packages  
	pip install -r requirements.txt


google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/selenium"
https://www.rezultati.com/utakmica/tenis/xbXu8lHU/#/detalji/detalji
https://www.atptour.com/en/scores/results-archive?tournamentType=ch


znaci u terminalu se pokrene ova naredba da se otvori chrome
zatim se ode na ovaj atp_tour i nade se match i matchBeats i tamo onda pokrenut skriptu i to ce se spremit u postgrebazu, rezulati scrape ne radi trenutno, sada radim na tome da skripta se moze cijelo vrijeme vrtit i da se onda moze samo maknut na stats i da se i to pokupi

--nista od ovoga i ovo se tretira kao scrape

postgre imam lokalhost 127.0.0.1 macinger/1324 







--OVO JE ZA ODDSPORTAL KAKO TREBA SCRAPEAT AKO SE BUDE MOGLO
https://www.oddsportal.com/tennis/chile/atp-santiago-2024/results/


body
app
w-full
relative
min-md:min-h-[100px] min-h-[89px] --ovo je drugi po redu element iz liste
flex
text-[22px] flex flex-wrap relative items-center font-secondary tournament-md:!text-[18px] tournament-m:!text-[17px] text-black-main font-bold leading-[42px] max-md:leading-[30px] sport-country-tournament
<h1>ATP Santiago (clay) Results, Scores &amp; Historical Odds <i class="bg-fav_star icon-left star-icon toggle-my-leagues order-last ml-2 inline-block max-h-[20px] min-h-[20px] min-w-[20px] cursor-pointer !bg-contain bg-center bg-no-repeat"></i></h1>

--ime turnira


body
app
w-full
relative
flex flex-col min-sm:px-3 max-md:mx-s0 max-md:mt-3 --treci poredu element iz liste
flex
flex flex-wrap gap-2 py-3 text-xs max-mm:flex-nowrap max-mm:overflow-x-auto max-mm:overflow-hidden max-md:mx-3 max-sm:!hidden no-scrollbar
--to je sad lista ali treba uzet onaj element koji je active 
flex items-center justify-center h-8 px-3 bg-gray-medium cursor-pointer active-item-calendar

--godina turnira


body
app
w-full
relative
class="flex flex-col px-3 text-sm max-mm:px-0"
--ovo je cetvrti po redu eleemnt iz liste
min-h-[80vh]   --samo ovaj element
data-v-f69a8221 --koji u sebi ima data ili, samo je ovaj element 
--sad je tu lista svega i svacega i treba proc kroz tu listu i nac unutar svakog tog elementa border-black-borders
group flex
next-m:flex next-m:!mt-0 ml-2 min-h-[32px] w-full hover:cursor-pointer --ovo je prvi element toga ima a
--prvi element toga treba uzet
--zatim drugi toga class="flex w-full items-center
data-testid="event-participants"
--prvi element je ovaj ispod
<div data-v-23626bce="" class="h-[16px] w-[22px] min-w-[22px] min-mt:order-3"><img data-v-23626bce="" src="https://cci2.oddsportal.com/country-flags/cl.svg" alt="cl" class="h-full w-full border border-gray-medium bg-no-repeat object-cover" loading="lazy"></div>
--a element je tu i ima 3 diva
	<div data-v-23626bce="" class="min-w-0 whitespace-nowrap group-hover:underline min-md:overflow-hidden"><p data-v-23626bce="" class="participant-name truncate">Tabilo A.</p></div> 
		<p data-v-23626bce="" class="participant-name truncate">Tabilo A.</p> --ovo je drugi i ima ime
	
--ponavljam samo za result	
--a element je tu i ima 3 diva	
--treci nema u sebi p nego je samo vrijednost

--ovo je za imena natjecatelja i result





body
app
w-full
relative
class="flex flex-col px-3 text-sm max-mm:px-0"
--ovo je cetvrti po redu eleemnt iz liste
min-h-[80vh]   --samo ovaj element
data-v-f69a8221 --koji u sebi ima data ili, samo je ovaj element 
--sad je tu lista svega i svacega i treba proc kroz tu listu i nac unutar svakog tog elementa border-black-borders
group flex
--drugi element je jedna kvota 
--u sebi ima dva div-a i p u kojem je kvota
--treci element je druga kvota



--kvote 

