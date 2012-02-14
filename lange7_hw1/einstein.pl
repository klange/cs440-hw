/*
* Einstein's Zebra Problem - CS 440 Spring 2012
* Kevin Lange
*
* A house is defined as an object which has five values:
*  - The nationality of the person in that house.
*  - The color of the house.
*  - The drink found within that house.
*  - The animal in the house.
*  - The cigarette brand smoked there.
*
* The "street" of houses ("Houses") is a list of
* these houses in their positions within the street. Thus, [_,_,X,_,_] means that X is the
* middle house (as opposed to some other location). As such, list operations can be used
* to show correlations between these locations (such as "the house with the kools is
* next to the house with the horse", or "the green house is to the right of the ivory house").
*/
drinks(X,Y) :- solve(Houses), member(house(X,_,Y,_,_), Houses).
smokes(X,Y) :- solve(Houses), member(house(X,_,_,_,Y), Houses).
owns(X,Y)   :- solve(Houses), member(house(X,_,_,Y,_), Houses).
livesIn(X,Y):- solve(Houses), member(house(X,Y,_,_,_), Houses).

/* A house is next to another house if it is right of the other (or vice-versa) */
nextTo(X, Y, List) :- rightOf(X,Y,List); rightOf(Y,X,List).

/* The problem definition makes use of "Right of", thus we define that here... */
rightOf(Left, Right, [Left | [ Right | _]]).
rightOf(Left, Right, [_ | Rest]) :- rightOf(Left, Right, Rest).

/* The problem statement itself */
solve(Houses) :-
	Houses = [_firstHouse,_,_middleHouse,_,_], /* There are five houses */
	member(house(englishman,red,_,_,_), Houses), /* The Englishman lives in the red house */
	member(house(spaniard,_,_,dog,_), Houses), /* The Spaniard owns the dog */
	member(house(_,green,coffee,_,_), Houses), /* Coffee is drunk in the green house */
	member(house(ukranian,_,tea,_,_), Houses), /* The Ukranian drinks tea */
	rightOf(house(_,green,_,_,_), house(_,ivory,_,_,_), Houses), /* The green house is right of the ivory house */
	member(house(_,_,_,snails,old_gold), Houses), /* The Old Gold smoker owns snails */
	member(house(_,yellow,_,_,kools), Houses), /* The Kools smoker lives in the yellow house */
	house(_,_,milk,_,_) = _middleHouse, /* Milk is drunk in the middle house */
	house(norwegian,_,_,_,_) = _firstHouse, /* The Norwegian lives in the first house */
	nextTo(house(_,_,_,_,chesterfields),house(_,_,_,fox,_), Houses), /* The man who smokes chesterfields is in the house next to the man who owns a fox */
	nextTo(house(_,_,_,_,kools),house(_,_,_,horse,_), Houses), /* The man who smokes kools is in the house next to the man who owns a horse */
	member(house(_,_,orange_juice,_,lucky_strike), Houses), /* The Lucky Strike smoker drinks orange juice */
	member(house(japanese,_,_,_,parliaments), Houses), /* The Japanese smokes parliaments */
	nextTo(house(norwegian,_,_,_,_), house(_,blue,_,_,_), Houses), /* The Norwegian is next to the blue house */
	member(house(_,_,water,_,_), Houses),  /* Someone drinks water... */
	member(house(_,_,_,zebra,_), Houses).  /* Someone owns a zebra... */

