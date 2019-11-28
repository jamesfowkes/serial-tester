static const int PIN_5V = 2;
static const int PIN_3V3 = 3;
static const int PIN_TX = 4;
static const int PIN_RX = 5;
static const int PIN_GND = 6;
static const int PIN_RTS = 7;
static const int PIN_CTS = 8;
static const int PIN_DTR = 9;
static const int PIN_DSR= 10;
static const int PIN_DCD = 11;
static const int PIN_RI = 12;

static String s_cmd_buffer;

static char handle_read_command(String& cmd)
{
	char result = '0';
	
	if (cmd == "5V")
	{
		result = digitalRead(PIN_5V) == HIGH ? '1' : '0';
	}

	else if (cmd == "3V3")
	{
		result = digitalRead(PIN_3V3) == HIGH ? '1' : '0';
	}

	else if (cmd == "GND")
	{
		result = digitalRead(PIN_GND) == HIGH ? '1' : '0';
	}

	else if (cmd == "RTS")
	{
		result = digitalRead(PIN_RTS) == HIGH ? '1' : '0';
	}

	else if (cmd == "DTR")
	{
		result = digitalRead(PIN_DTR) == HIGH ? '1' : '0';
	}

	return result;
}

static char handle_write_command(String& cmd, int hi_lo)
{

	if (cmd == "CTS")
	{
		digitalWrite(PIN_CTS, hi_lo);
	}
	else if (cmd == "DSR")
	{
		digitalWrite(PIN_DSR, hi_lo);
	}
	else if (cmd == "DCD")
	{
		digitalWrite(PIN_DCD, hi_lo);
	}
	else if (cmd == "RI")
	{
		digitalWrite(PIN_RI, hi_lo);
	}
	
	return '1';
}

static char handle_command(String& cmd)
{
	String target;
	
	char result = '0';

	if (cmd.startsWith("READ."))
	{
		target = cmd.substring(5);
		result = handle_read_command(target);
	}
	else if (cmd.startsWith("WRITE1."))
	{
		target = cmd.substring(7);
		result = handle_write_command(target, HIGH);
	}
	else if (cmd.startsWith("WRITE0."))
	{
		target = cmd.substring(7);
		result = handle_write_command(target, LOW);
	}
	else
	{
		Serial.print("Command '");
		Serial.print(cmd);
		Serial.println("' not recognised");
	}
	
	return result;
}

void setup()
{
	pinMode(PIN_5V, INPUT);
	pinMode(PIN_3V3, INPUT);
	pinMode(PIN_TX, INPUT);
	pinMode(PIN_RX, INPUT);
	pinMode(PIN_GND, INPUT);

	pinMode(PIN_RTS, INPUT);
	pinMode(PIN_CTS, OUTPUT);
	pinMode(PIN_DTR, INPUT);
	pinMode(PIN_DSR, OUTPUT);
	pinMode(PIN_DCD, OUTPUT);
	pinMode(PIN_RI, OUTPUT);

	Serial.begin(115200);
}

void loop()
{
	while(Serial.available())
	{
		char c = Serial.read();

		if (c == '\n')
		{
			char res = handle_command(s_cmd_buffer);
			Serial.println(res);
			s_cmd_buffer = "";
		}
		else
		{
			s_cmd_buffer += c;	
		}
	}
}