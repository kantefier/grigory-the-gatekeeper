package main

import (
	"log"
	"os"
	"strconv"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

func main() {
	log.SetFlags(log.LstdFlags | log.LUTC | log.Lmicroseconds)
	log.Println("Starting Grigory...") //TODO: add version?

	// Read some ENV variables

	// BOT_TOKEN is essential to authorize
	token, is_found := os.LookupEnv("BOT_TOKEN")
	if !is_found {
		log.Fatalf(`Env BOT_TOKEN is not defined, unable to start`)
	}

	// BOT_DELAY_SECONDS is optional. It sets the delay between calls to Waves Exchange API
	// Default value is 60
	requestDelay := 60
	if delayStr, is_found := os.LookupEnv("BOT_DELAY_SECONDS"); is_found {
		delayInt, err := strconv.Atoi(delayStr)
		if err != nil {
			log.Printf(`ERROR: Failed to parse BOT_DELAY_SECONDS Env as an int: "%s"`, delayStr)
			log.Printf(`Going to use default value of 60 seconds`)
		} else {
			requestDelay = delayInt
		}
	}

	bot, err := tgbotapi.NewBotAPI(token)
	if err != nil {
		log.Panic(err)
	}

	bot.Debug = true

	for {
		// should I write an infinite loop? Just like the Py version?
	}
}
