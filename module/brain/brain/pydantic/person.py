from langchain_core.pydantic_v1 import BaseModel, Field, Extra

class BasicInformation(BaseModel, extra=Extra.allow):
    user_name: str = Field(description="The online user name of the person")
    real_name: str = Field(description="The real full name of the person")
    age: int = Field(description="The age of the person")
    gender: str = Field(description="The gender of the person")
    location: str = Field(description="The current living location of the person")
    languagesSpoken: str = Field(description="Languages the person speaks, separated by commas")

class PersonalityAndInterests(BaseModel, extra=Extra.allow):
    hobbiesAndInterests: str = Field(description="List of hobbies and interests, separated by commas")
    favoriteBooks: str = Field(description="List of favorite books, separated by commas")
    favoriteMovies: str = Field(description="List of favorite movies, separated by commas")
    favoriteGames: str = Field(description="List of favorite games, separated by commas")
    favouriteMusicGenres: str = Field(description="List of favorite music genres, separated by commas")
    favoriteArtists: str = Field(description="List of favorite artists, separated by commas")
    occupation: str = Field(description="Current occupation of the person")
    industryKnowledge: str = Field(description="Areas of industry knowledge, separated by commas")
    professionalGoals: str = Field(description="Professional goals and aspirations")
    dailyRoutines: str = Field(description="Daily routines or habits")
    preferredCuisines: str = Field(description="Preferred cuisines")
    travelExperiences: str = Field(description="Travel experiences, separated by commas")
    dreamDestinations: str = Field(description="Dream travel destinations, separated by commas")
    twitter: str = Field(description="Twitter handle of the person")
    instagram: str = Field(description="Instagram username of the person")
    linkedin: str = Field(description="LinkedIn profile URL of the person")
    sentimentAnalysisCurrentMood: str = Field(description="Current mood based on sentiment analysis")
    sentimentAnalysisCommonEmotions: str = Field(description="Common emotions based on sentiment analysis, separated by commas")

class LifeContext(BaseModel, extra=Extra.allow):
    educationLevel: str = Field(description="Highest level of education attained")
    relationshipStatus: str = Field(description="Current relationship status")
    lifeGoalsAndAspirations: str = Field(description="Life goals and aspirations")
    valuesAndBeliefs: str = Field(description="Core values and beliefs")

class Profile(BaseModel, extra=Extra.allow):
    basicInformation: BasicInformation = Field(description="Basic information about the person")
    personalityAndInterests: PersonalityAndInterests = Field(description="Personality traits and interests")
    lifeContext: LifeContext = Field(description="Context of the person's life")
    dislikedTopics: str = Field(description="Topics the person dislikes, separated by commas")
