// Settings
const bool rotating = false;
const bool waterfall = false;

// For timing purposes
volatile float microsPerPixel;
volatile float nextPixelMicros = 0;
volatile bool interrupted = false;
volatile int32_t currentPixel = 0;
volatile int32_t startPixel = 0;
elapsedMicros sinceMagnet;
volatile bool running = false;

// To access the right board/LED
volatile uint32_t offsetPixel = 0;
volatile uint32_t currentBoard = 0;

// How much the height value is shifted. Changes each rev.
volatile uint32_t boardOffset = 0;

// currentBoard + boardOffset
volatile uint32_t offsetBoard;
volatile uint32_t evenRotation = false;

const uint32_t latchPin = 5;
const uint32_t outputEnable = 4;
const uint32_t hallpin = 20;

SPISettings mySettings(48000000, LSBFIRST, SPI_MODE0);


void setup(void)
{
	// Setup I/O
	pinMode(hallpin, INPUT_PULLUP);
	pinMode(outputEnable, OUTPUT);
	pinMode(latchPin, OUTPUT);
	digitalWrite(outputEnable, LOW);

	SPI.begin();

	// call timerUpdate whenever the sensor is over the magnet
	attachInterrupt(hallpin, timerUpdate, FALLING);
}

void loop(void)
{
	// Continuously chech if we should refresh the LED data
	if (running && (sinceMagnet > nextPixelMicros))
	{
		sendData();
	}
}

void timerUpdate(void)
{
	// Set a flag that is read at the end of sendData so it knows if it's
	// been interrupted
	interrupted = true;
	running = true;

	// Calculate the new pixel duration
	microsPerPixel = ((float) sinceMagnet) / 100.0;

	// Reset timer & wait half a period before the first LED refresh 
	sinceMagnet = 0;
	nextPixelMicros = 0;

	// Always 0 if !rotating, sawtooth from 0 to 99 otherwise
	currentPixel = startPixel;

	// Let the image "fall down"
	if (waterfall && evenRotation)
	{
		// Sawtooth from 9 to 0
		if (boardOffset == 0)
		{
			boardOffset = 10;
		}

		boardOffset--;
	}

	evenRotation = !evenRotation;

	// Let the image rotate counterclockwise
	if (rotating)
	{
		// Sawtooth from 0 to 99
		startPixel++;
		startPixel %= 100;
	}
}

void sendData(void)
{
	// Reset the interrupted flag
	interrupted = false;

	SPI.beginTransaction(mySettings);

	// Send the data, taking into account the vertical board offset in
	// case waterfall is enabled. Return if there's been an interrupt
	// to not send any unnecessary data.
	for (int i = 0; i < 5; i++)
	{
		if (interrupted) return;

		currentBoard = 2*i;
		offsetBoard = (currentBoard + boardOffset) % 10;
		offsetPixel = (currentPixel + 8*i + 70) % 100;

		for (int j = 5; j >= 0; j--)
		{
			SPI.transfer(image[offsetPixel][offsetBoard][j]);
		}


		if (interrupted) return;

		currentBoard++;
		offsetBoard = (currentBoard + boardOffset) % 10;
		offsetPixel = (offsetPixel + 50) % 100;

		for (int j = 5; j >= 0; j--)
		{
			SPI.transfer(image[offsetPixel][offsetBoard][j]);
		}
	}

	SPI.endTransaction();
	pulseLatch();

	// Only modify the global timing variables if no interrupt has been fired
	// while this function was running. Otherwise we're executing code from the
	// old revolution when the new one has already started, and the image becomes
	// jittery.
	if (!interrupted)
	{
		currentPixel++;
		nextPixelMicros += microsPerPixel;
	}
}

// Short pulse on the latch pin in order to send the data from the LED driver's
// data transmission registers to the output registers
inline void pulseLatch(void)
{
	digitalWrite(latchPin, HIGH);
	delayMicroseconds(1);
	digitalWrite(latchPin, LOW);
}
