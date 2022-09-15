/*! 
 * \file   kh4server.c  Khepera4 server application              
 *
 * \brief 
 *         This is application waits for Khepera 4 commands A-Z received from serial port
 *				 usage: kh4server [serial_port (optional)]	 
 *         
 *        
 * \author   Julien Tharin (K-Team SA)   - Modified by Louis L'Haridon                             
 *
 * \note     Copyright (C) 2012 K-TEAM SA - ETIS LAB (UMR CNRS 8051)
 * \bug      none discovered.                                         
 * \todo     nothing.
 */

#include <khepera/khepera.h>
#include <signal.h>
#include <limits.h>

#define MAXBUFFERSIZE 128

//#define DEBUG

// serial parameters
#define BAUDRATE B115200
#define VAL_BAUDRATE 115200
#define SERIAL_PORT "/dev/ttyS0" // fake serial port
// parameters for serial transmission
enum {
  Timeout = 800, // ms
  LineLength = 16 + 64 + 1 + 1 + 1,
};

#define ERROR_CMD_CHAR '$'


#define MAX_ARG 16
#define ARG_LENGTH 10
typedef  char string[ARG_LENGTH];

static int porthandle=-1;

static int quitReq = 0;
static char buf[1024];


/*! handle to the various khepera4 devices (knet socket, i2c mode)
 */
static knet_dev_t * dsPic;

int process_command (); // function declaration

/*--------------------------------------------------------------------*/
/*!
 * Intercept the ctrl-c
 *
 * \param sig signal
 *
 * \return none
 */
static void ctrlc_handler( int sig ) 
{
  quitReq = 1;

}


/*--------------------------------------------------------------------*/
/*! Kbhit helper function
 *
 * \return A value :
 *      - 1 Character pending 
 *      - 0 no character
 *			- -1 error
 */
int kbhit(void)
{
	struct timeval tv;
	fd_set read_fd;  /* Do not wait at all, not even a microsecond */
  
  tv.tv_sec=0;
  tv.tv_usec=0;  /* Must be done first to initialize read_fd */
  FD_ZERO(&read_fd);  /* Makes select() ask if input is ready:   *
                         0 is the file descriptor for stdin      */
  FD_SET(0,&read_fd);  /* The first parameter is the number of the *
                          largest file descriptor to check + 1. */
  if(select(1, &read_fd, NULL, /*No writes*/ NULL, /*No exceptions*/
&tv) == -1)
    return -1; /* An error occured */

  /* read_fd now holds a bit map of files that are   *
     readable. We test the entry for the standard    *
     input (file 0). */
  if(FD_ISSET(0,&read_fd))    /* Character pending on stdin */
    return 1; 
    
    
  /* no characters were pending */
  
  return 0;

} 

/*--------------------------------------------------------------------*/
/*! clear screen
 *
 * \return none
 *   
 */
void clear_screen()
{
	printf ("\33[2J" );
}

/*--------------------------------------------------------------------*/
/*! connect to serial port
 *
 * \param device device name
 * \param baudrate baudrate
 * \return >=0 : Ok; -1 : cannot open serial port
 *
*/ 
static int com_connect(const char* device, speed_t baudrate) {

	struct termios options;
	int HComm=-1; // handle to the port where the sensor is connected 

	if ((HComm=open(device,O_RDWR | O_NOCTTY | O_NDELAY))<0) {
		printf("ERROR: can't open serial port %s\n",device);
		return -1;
	}

	fcntl(HComm, F_SETFL, 0); // blocking input

	/* get the current options */
	tcgetattr(HComm, &options);

	/* set raw input, 0 second timeout */
	options.c_cflag     |= (CLOCAL | CREAD);
	// options.c_lflag     &= ~(ICANON | ECHO | ECHOE | ISIG);
	
	
	options.c_lflag = ICANON;

	
	options.c_oflag     &= ~OPOST;
	options.c_cc[VMIN]  = 1;//0; // wait 1 char
	options.c_cc[VTIME] = 0; //Timeout/100; // timeout in 1/10 of second

	// setbaudrate
	cfsetispeed(&options, baudrate);
	cfsetospeed(&options, baudrate);

	/* set the options */
	tcsetattr(HComm, TCSANOW, &options);

  return HComm;
}

/*--------------------------------------------------------------------*/

/*!
 * write to serial port
 *
 * \param data data to be sent to the port
 * \param size size of the data
 *
 * \return number of written char
*/
static int com_send(const char* data, int size) {
  int n;

   tcflush (porthandle, TCIFLUSH); // clear the read/write buffer
   n=write( porthandle , data , size );

  return n;
}


/*--------------------------------------------------------------------*/
/*!
 * receive data from serial port
 *
 * \param data data to be sent to the port
 * \param max_size max size of the data variable
 * \param timeout timeout in [ms]
 *
 * \return number of data read
*/
static int com_recv(char* data, int max_size, int timeout) {

  int filled = 0;
  int readable_size = 0;
 	struct termios options;
 
 // fcntl(porthandle, F_SETFL, FNDELAY); // read will return immediately if no data

  memset (data, 0,max_size);

   do {
   // DWORD dwErrors;
   // COMSTAT ComStat;
   // ClearCommError(HComm, &dwErrors, &ComStat);

    ioctl(porthandle, FIONREAD, &readable_size); // get number of bytes available to be read

    int read_n = (readable_size > max_size) ? max_size : readable_size;

    int n;
    
    n=read( porthandle , &data[filled] ,read_n );
    filled += n;
    readable_size -= n;

    if (filled >= max_size) {
      return filled;
    }
  } while (readable_size > 0);

  // tcflush (HComm, TCIFLUSH); // clear the read buffer
 

  if (timeout > 0) {

	 /* get the current options */
	//	tcgetattr(porthandle, &options);
		options.c_cc[VTIME] = timeout/100; // timeout in tenth of second

		/* set the options */
	//	tcsetattr(porthandle, TCSANOW, &options);


	//	fcntl(porthandle, F_SETFL, 0); // blocking with timeout

		int n;
		while (1) {

			n=read(porthandle, &data[filled], 1);
			if (n < 1) {

				tcflush (porthandle, TCIFLUSH); // clear the read buffer

				return filled;
			}
			filled += n;
			if (filled >= max_size) {
				return filled;
			}
		
		}
  }
}

/*--------------------------------------------------------------------*/
/*
/*!
 * Read data (Reply) until the termination
 *
 *  \param buffer read data
 *
 *  \return return the number of the count of the read data
*/
static int readLine(char *buffer) {

  int i;
  for (i = 0; i < LineLength -1; ++i) {
    char recv_ch;
    int n = read(porthandle, &recv_ch, 1);// com_recv(&recv_ch, 1, Timeout);
    //printf("rec_ch :%c\n",recv_ch);
    if (n <= 0) {
      if (i == 0) {
				return -1;		// timeout
      }
      break;
    }
    if ((recv_ch == '\r') || (recv_ch == '\n')) {
      break;
    }
    buffer[i] = recv_ch;
  }
  
  buffer[i] = '\0';

	//printf("readLine:%s\n", buffer);
	
  return i;
}

/*--------------------------------------------------------------------*/
/*! initMot initializes then configures the motor control
 * unit.
 *
 * \param hDev device handle
 * \return A value :
 *      - 0 if success
 *      - -1 if any error
 *
 */
int initMot(knet_dev_t *hDev)
{
  if(hDev)
  {
		/* initialize the motors controlers*/
		 
		/* tuned parameters */
		kh4_SetPositionMargin(20 ,hDev ); 				// position control margin
		kh4_ConfigurePID( 10 , 5 , 1,hDev  ); 		// P,I,D
		kh4_SetSpeedProfile(3,0,20,1,400,hDev ); // Acceleration increment ,  Acceleration divider, Minimum speed acc, Minimum speed dec, maximum speed
		
		kh4_SetMode( kh4RegIdle,hDev );  				// Put in idle mode (no control)

	  return 0;
  }
  else
  {
	  printf("initMot error, handle cannot be null\r\n");
	  return -1;
  }
}


/*--------------------------------------------------------------------*/
/*! initKH4 initialize various things in the kh4 then
 * sequentialy open the various required handle to the three i2c devices 
 * on the khepera3 using knet_open from the knet.c libkhepera's modules.
 * Finaly, this function initializes then configures the motor control
 * unit.
 *
 * \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int initKH4( void )
{
  /* This is required */
  kh4_init(0,NULL);
  
  /* open various socket and store the handle in their respective pointers */
 	dsPic  = knet_open( "Khepera4:dsPic" , KNET_BUS_I2C , 0 , NULL );

  if(dsPic!=0)
  {

    return initMot(dsPic);
  }

  return -1;
     
 } 

/*--------------------------------------------------------------------*/
/*! Init mot or reset motor controller
 *
 * \param narg number of argument
 * \param larg argument array
 *
 * \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int InitMot(int narg,string *larg)
{
	int rc;
	char Buffer[MAXBUFFERSIZE];

  if(dsPic!=0)
  {
    initMot(dsPic);
    sprintf(Buffer,"m\r\n");
		com_send(Buffer,strlen(Buffer));
    return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));	
	return -1;
}	


/*--------------------------------------------------------------------*/
/*! proxIR retrieves proximity ir measure using kb_khepera4.c library.
 *
 * \param narg number of argument
 * \param larg argument array
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ReadProxSensors(int narg, string *larg)
{
  char Buffer[MAXBUFFERSIZE];
  char BufferOut[MAXBUFFERSIZE];
  int sensor,i;
  

	sprintf(BufferOut,"n");

	if(kh4_proximity_ir((char *)Buffer, dsPic)>=0)
	{	
		for (i=0;i<12;i++)
		{
			sensor=(Buffer[i*2] | Buffer[i*2+1]<<8);
			sprintf(BufferOut+strlen(BufferOut),",%d",sensor);
			
		}																		

		sprintf(Buffer,"%s\r\n",BufferOut);	
  	com_send(Buffer, strlen(Buffer));
		
		
		#ifdef DEBUG
			printf("\nReadProxSensors : %s\n",BufferOut);
		#endif	
		return 0;	
	}
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;			
}
		
/*--------------------------------------------------------------------*/
/*! ambIR retrieves ambiant ir measure using kb_khepera4.c library.
 *
 * \param narg number of argument
 * \param larg argument array
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ReadAmbSensors(int narg, string *larg)
{
  char Buffer[MAXBUFFERSIZE];
  char BufferOut[MAXBUFFERSIZE];
  int sensor,i;
  

	sprintf(BufferOut,"o");

	if(kh4_ambiant_ir((char *)Buffer, dsPic)>=0)
	{	
		for (i=0;i<12;i++)
		{
			sensor=(Buffer[i*2] | Buffer[i*2+1]<<8);

			sprintf(BufferOut+strlen(BufferOut),",%d",sensor);
				
		}
	

		sprintf(Buffer,"%s\r\n",BufferOut);	
  	com_send(Buffer, strlen(Buffer));
		#ifdef DEBUG
			printf("\nReadAmbSensors : %s\n",Buffer);
		#endif	
		return 0;	
	}
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;	
}

/*--------------------------------------------------------------------*/
/*! batStatus retrieves the battery status using kb_khepera4.c library.
 *
 * \param narg number of argument
 * \param larg state to inquire
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int batStatus(int narg, string *larg)
{
  char Buffer[MAXBUFFERSIZE];
  char BufferOut[MAXBUFFERSIZE];
  short argument;

	if (narg != 1)
	{
		sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
		com_send(Buffer, strlen(Buffer));
		return -1;
	}

  argument = atoi(larg[0]);
  
	#ifdef DEBUG
		printf("\nbatStatus argument : %d (%s)\n",argument,larg[0]);
	#endif
  
  if(kh4_battery_status(Buffer,dsPic)>=0){
		switch(argument){
			case 0:		/* Read Voltage [mV] */
				 sprintf(BufferOut,"v,%.0f\r\n",(Buffer[10] | Buffer[11]<<8)*9.76);
				break;
			case 1:		/* Read Current [mA]*/
					sprintf(BufferOut,"v,%.0f\r\n",(short)(Buffer[4] | Buffer[5]<<8)*0.07813);
				break;
			case 2:		/* Read Average Current [mA]*/
				sprintf(BufferOut,"v,%.0f\r\n",(short)(Buffer[6] | Buffer[7]<<8)*0.07813);
				break;
			case 3:		/* Read absolute remaining capacity [mAh]*/
				sprintf(BufferOut,"v,%.0f\r\n",(Buffer[1] | Buffer[2]<<8)*1.6);
				break;
			case 4:		/* Read Temperature [C]*/
				sprintf(BufferOut,"v,%.1f\r\n",(short)(Buffer[8] | Buffer[9]<<8)*0.003906);
				break;
			case 5:		/* Read relative remaining capacity */
				 sprintf(BufferOut,"v,%d\r\n",Buffer[3]);
				break;
			case 6:		/* charger plugged */
				 sprintf(BufferOut,"v,%d\r\n",kh4_battery_charge(dsPic));
				break;
			case 7:		/* status */
				 sprintf(BufferOut,"v,%d\r\n",Buffer[0]);
				break;	

			default:
				sprintf(BufferOut,"%c\r\n",ERROR_CMD_CHAR);
				
				
		} // switch
		com_send(BufferOut,strlen(BufferOut));
		return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));  
  return -2;

}



/*--------------------------------------------------------------------*/
/*! revisionOS retrieves the khepera4 os version using kb_khepera4.c library.
 *
 * \param narg number of argument
 * \param larg array of argument
 *
 * \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int revisionOS(int narg, string *larg)
{
  char Buffer[MAXBUFFERSIZE];	/* buffer that handle the returned datas from kh4 */
  unsigned int ver ;


  if(kh4_revision((char *)Buffer, dsPic)==0){
  
  	sprintf(Buffer,"b,%c,%d\r\n",(Buffer[0]>>4) +'A',Buffer[0] & 0x0F);
  	com_send(Buffer, strlen(Buffer));
   
		return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));  
  return -1;
}

 
/*--------------------------------------------------------------------*/
/*! measureUS retrieves ultrasonic measure from all the transceiver.
 *
 *	\param argc number of argument 	
 *  \param argv array of argument
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 *  
 */
int GetUS( int argc, string * argv)
{
  char Buffer[MAXBUFFERSIZE],buf[MAXBUFFERSIZE];
  
  int i;
 
  if(kh4_measure_us((char *)Buffer,  dsPic)>=0)
  {
   
		sprintf(buf,"g");
		
		for (i=0;i<5;i++) {
			sprintf(buf+strlen(buf),",%d",Buffer[i*2] | Buffer[i*2+1]<<8);
		}	
		
		sprintf(Buffer,"%s\r\n",buf);	
  	com_send(Buffer, strlen(Buffer));
		
		return 0;
	} 
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));	
	return -2;
	
}


/*--------------------------------------------------------------------*/
/*! SetSpeed set the motor controller speed in the engine control unit.
 *
 *	\param argc number of argument	
 *  \param argv first param (argv[0]) is the motor1 speed.
 *   						2nd second param (argv[1]) is the motor2 speed.
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int SetSpeed( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
	
	#ifdef DEBUG
		printf("\nSetSpeed : argv[0] %s %d argv[1] %s %d",argv[0],atoi(argv[0]),argv[1],atoi(argv[1]));
	#endif	
	
	kh4_SetMode(kh4RegSpeed,dsPic );
	if (kh4_set_speed(atol(argv[0]),atol(argv[1]), dsPic)>=0) {

		sprintf(Buffer,"d\r\n");
		com_send(Buffer, strlen(Buffer));
	
		return 0;
	}
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}

/*--------------------------------------------------------------------*/
/*! SetSpeedOpenLoop set the motor controller speed in the engine control unit.
 *
 *	\param argc number of argument	
 *  \param argv first param (argv[0]) is the motor1 speed.
 *   						2nd second param (argv[1]) is the motor2 speed.
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int SetSpeedOpenLoop( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
	
	if(dsPic!=0)
  {
		kh4_SetMode(kh4RegSOpenLoop,dsPic );
		kh4_set_speed(atol(argv[0]),atol(argv[1]), dsPic);
	
		sprintf(Buffer,"l\r\n");
		com_send(Buffer, strlen(Buffer));
  	
		return 0;
	}
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}


/*--------------------------------------------------------------------*/
/*! Getspeed get the measurement of the speed
 *
 *	\param argc number of argument	
 *  \param argv array of argument
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int GetSpeed( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
	int left,right; 

  if(dsPic!=0)
  {
  	
  	kh4_get_speed(&left,&right,dsPic );
    
   	#ifdef DEBUG
   		printf("\nGetSpeed : left %d right %d",left,right);
   	#endif
  	 	
  	sprintf(Buffer,"e,%d,%d\r\n",left,right);
  	com_send(Buffer, strlen(Buffer));
  	
		return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));

	return -1;
}

/*--------------------------------------------------------------------*/
/*! SetTargetProfile configures the motor controller position in the engine control unit using the PID and speed/accel profile.
 *
 *	\param argc number of argument
 *  \param argv first param (argv[0]) is the motor1 position.
 *  						second param (argv[1]) is the motor2 position.
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int SetTargetProfile( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
  if(dsPic!=0)
  {
  	kh4_SetMode(kh4RegPosition,dsPic );
		kh4_set_position(atol(argv[0]),atol(argv[1]), dsPic);
  	sprintf(Buffer,"f\r\n");
  	com_send(Buffer, strlen(Buffer));
	return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}


/*--------------------------------------------------------------------*/
/*! ResetEncPosition set encoder position
 *
 *	\param argc number of argument
 *  \param argv argument array
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ResetEncPosition( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
	
  if(dsPic!=0)
  {
  	
  	kh4_ResetEncoders(dsPic);
  	
  	sprintf(Buffer,"i\r\n");
  	com_send(Buffer, strlen(Buffer));
	return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}

/*--------------------------------------------------------------------*/
/*! GetMotPos get the motor position.
 *	
 *	\param argc number of argument
 *  \param argv first param (argv[0]) is the motor1 position.
 *  						second param (argv[1]) is the motor2 position.
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ReadPos( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
	int left,right; 
	
  if(dsPic!=0)
  {
  	
  	kh4_get_position(&left,&right,dsPic);
  	
  	#ifdef DEBUG
  		printf("\nReadPos : left %d right %d",left,right);
  	#endif	
  	
  	sprintf(Buffer,"r,%d,%d\r\n",left,right);
  	com_send(Buffer, strlen(Buffer));
  	
		return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}

/*--------------------------------------------------------------------*/
/*! GetGyro get measurement of gyroscope
 *	
 *	\param argc number of argument
 *  \param argv argument array
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ReadGyro( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
	int i;
	
  if(dsPic!=0)
  {
  	
  	kh4_measure_gyro(Buffer, dsPic);
  	
  	sprintf(buf,"s");
		
		for (i=0;i<30;i++) {
			sprintf(buf+strlen(buf),",%d",(short)(Buffer[i*2] | Buffer[i*2+1]<<8));
		}
		
		sprintf(Buffer,"%s\r\n",buf);	
  	com_send(Buffer, strlen(Buffer));
  	
		return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}

/*--------------------------------------------------------------------*/
/*! ReadAccel get measurement of accelerometer
 *	
 *	\param argc number of argument
 *  \param argv argument array
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ReadAccel( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
	int i;
	
  if(dsPic!=0)
  {
  	
  	kh4_measure_acc(Buffer, dsPic);
  	
  	sprintf(buf,"t");
		
		for (i=0;i<30;i++) {
			sprintf(buf+strlen(buf),",%d",(short)(Buffer[i*2] | Buffer[i*2+1]<<8));
		}	
		
  	sprintf(Buffer,"%s\r\n",buf);	
  	com_send(Buffer, strlen(Buffer));
  	
		return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}
/*--------------------------------------------------------------------*/
/*! Configure PID
 *	
 *	\param argc number of argument
 *  \param argv first param (argv[0]) is the Kp parameter
 *  						second param (argv[1]) is the Ki parameter
 *  						third param (argv[2]) is the Kd parameter
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ConfigPID( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
  if(dsPic!=0)
  {	  	
  	kh4_ConfigurePID( atoi(argv[0]) , atoi(argv[1]) , atoi(argv[2]),dsPic  ); 		// configure P,I,D
   	sprintf(Buffer,"h\r\n");
  	com_send(Buffer, strlen(Buffer));
	return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;	
}

/*--------------------------------------------------------------------*/
/*! configure speed and acceleration profiles
 *
 *	\param argc number of argument	
 *  \param argv first param (argv[0]), Acceleration increment ,  Acceleration divider, Minimum speed acc, Minimum speed dec, maximum speed
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ConfigSpeedProfile( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
  if(dsPic !=0)
  {
  	kh4_SetSpeedProfile(atoi(argv[0]),atoi(argv[1]),atoi(argv[2]),atoi(argv[3]),atoi(argv[4]),dsPic );
  	
  	sprintf(Buffer,"j\r\n");
  	com_send(Buffer, strlen(Buffer));
	return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}  


/*--------------------------------------------------------------------*/
/*! configure position margin
 *
 *	\param argc number of argument	
 *  \param argv first param (argv[0]) position margin
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ConfigPosMargin( int argc, string *argv)
{
	char Buffer[MAXBUFFERSIZE];
  if(dsPic !=0)
  {
  	kh4_SetPositionMargin(atoi(argv[0]),dsPic);
  	sprintf(Buffer,"p\r\n");
  	com_send(Buffer, strlen(Buffer));
	return 0;
  }
	sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
	com_send(Buffer, strlen(Buffer));
	return -1;
}  

/*--------------------------------------------------------------------*/
/*! set led
 *
 *	\param argc number of argument	
 *  \param argv first param (argv[0]) is led 0 R
 *              second param (argv[1]) is led 0 G
 								...
 								9th argument is led 2 B
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int SetLED(int argc,string * argv)
{
	int rc;
	char buf[MAXBUFFERSIZE];
  /* Frame format : { Size, Command, Terminator }
   * where the command can be more than 1 byte */

  if(dsPic)
  {
  	if (argc != 9)
		{
			sprintf(buf,"%c\r\n",ERROR_CMD_CHAR);
			com_send(buf, strlen(buf));
			return -1;
		}
  
		kh4_SetRGBLeds(atoi(argv[0]),atoi(argv[1]),atoi(argv[2]),atoi(argv[3]),atoi(argv[4]),atoi(argv[5]),atoi(argv[6]),atoi(argv[7]),atoi(argv[8]), dsPic);
		
		sprintf(buf,"k\r\n");
		com_send(buf, strlen(buf));
		
		return rc;
  }
	
	sprintf(buf,"%c\r\n",ERROR_CMD_CHAR);
	com_send(buf, strlen(buf));
	return -2;
}	



/*--------------------------------------------------------------------*/
/*! Configure US sensors
 *
 *	\param argc number of argument	
 *  \param argv arg[0] mask of the activated sensors
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ConfigUs(int argc,string * argv) {
	char buf[MAXBUFFERSIZE];
	if(dsPic)
  {
		kh4_activate_us(atoi(argv[0]),dsPic);
		sprintf(buf,"u\r\n");
		com_send(buf, strlen(buf));
		return 0;
	}
	sprintf(buf,"%c\r\n",ERROR_CMD_CHAR);
	com_send(buf, strlen(buf));	
	return -1;
}	

/*--------------------------------------------------------------------*/
/*! Reset Micro controller
 *
 *	\param argc number of argument	
 *  \param argv array of argument
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
 */
int ResetMicro(int argc,string * argv) {
	char buf[MAXBUFFERSIZE];
	if(dsPic)
  {
		kh4_SetStatusLeds(KH4_ST_LED_RED_ON, dsPic);
		usleep(10000); // wait 10ms
		kh4_reset(dsPic);
		sprintf(buf,"z\r\n");
		com_send(buf, strlen(buf));
		return 0;
	}
	sprintf(buf,"%c\r\n",ERROR_CMD_CHAR);
	com_send(buf, strlen(buf));	
	return -1;
}	
	  

/*--------------------------------------------------------------------*/
/*! Braintenberg demo program
 *
 *  \param none.
 */

#define BR_IRGAIN 3
#define fwSpeed 200//150
#define BMIN_SPEED 10

#define RotSpeedL 120
#define RotSpeedR -120

#define MAX_DIST 500
#define MIN_DIST 80 // 70

#define IMOBIL_SENS 250

#define IMOBIL_POS 30.0/KH4_PULSE_TO_MM
 
int braitenberg(int argc,string * argv)
{
  int Connections_B[8] = { -2, -3, -4, -9,  4,  3,  2, 1 }; // weight of every 8 sensor for the right motor 
  int Connections_A[8] = { 2,  3,  4, -7, -4, -3, -2, 1}; // weight of every 8 sensor for the left motor 

  int i, buflen, sensval;

  int lspeed, rspeed;
  int tabsens[8];
  int left_speed, right_speed;
  unsigned int immobility = 0;
  unsigned int prevpos_left, pos_left, prevpos_right,  pos_right;
  int sensors[8];
  char Buffer[256];
  int readable_size=0;
	int out=0;
  

	if (argc != 1)
	{
		sprintf(buf,"%c\r\n",ERROR_CMD_CHAR);
		com_send(buf, strlen(buf));
		return -1;
	}
	
	if (atoi(argv[0]) == 2 )
	{
		sprintf(buf,"a\r\n");
		com_send(buf, strlen(buf));
		return 1;
	} else
	{
		if ((atoi(argv[0]) == 0) || (atoi(argv[0]) == 1) )
		{
			// continue with below
		}
		else
		{
			sprintf(buf,"%c\r\n",ERROR_CMD_CHAR);
			com_send(buf, strlen(buf));
			return -1;
		}
	}
	
	sprintf(buf,"a\r\n");
	com_send(buf, strlen(buf));
	
	// configure acceleration slope
  kh4_SetSpeedProfile(10,0,20 ,1,400,dsPic ); // Acceleration increment ,  Acceleration divider, Minimum speed acc, Minimum speed dec, maximum speed
	kh4_SetMode(kh4RegSpeedProfile,dsPic );
	
  /* Get the current position values */
	kh4_get_position(&prevpos_left,&prevpos_right,dsPic);

	printf("\nBraitenberg mode; enter any serial command to stop\n");

	fcntl(porthandle, F_SETFL, FNDELAY); // read will return immediately if no data
  
  kh4_SetMode(kh4RegSpeedProfile,dsPic );
	
	
  do
  {
    lspeed = 0; rspeed = 0;
    
		// get ir sensor
		kh4_proximity_ir(Buffer, dsPic);
				 
		//limit the sensor values, don't use ground sensors
		for (i = 0; i < 8; i++)	
		{
			sensval = (Buffer[i*2] | Buffer[i*2+1]<<8);
			if(sensval > MAX_DIST)
				tabsens[i] = MAX_DIST;
			else if (sensval < MIN_DIST)
				tabsens[i] = 0;
			else
				tabsens[i] = (sensval-MIN_DIST)>>1;
			#ifdef DEBUG
			printf("%4d ",sensval);	
			#endif
		}

		

		for (i = 0; i < 8; i++)
		{
		  lspeed += Connections_A[i] * tabsens[i];
		  rspeed += Connections_B[i] * tabsens[i];				
		}

		left_speed = ((lspeed / BR_IRGAIN) + fwSpeed);
		right_speed = ((rspeed / BR_IRGAIN) + fwSpeed);

		if(left_speed >= 0 && left_speed < BMIN_SPEED)
		  left_speed = BMIN_SPEED;
		if(left_speed < 0 && left_speed > -BMIN_SPEED)
		  left_speed = -BMIN_SPEED;
		if(right_speed >= 0 && right_speed < BMIN_SPEED)
		  right_speed = BMIN_SPEED;
		if(right_speed < 0 && right_speed > -BMIN_SPEED)
		  right_speed = -BMIN_SPEED;


		kh4_set_speed(left_speed ,right_speed ,dsPic );
		
		#ifdef DEBUG
		printf("  sl: %4d  sr: %4d\n",left_speed ,right_speed);
		#endif
		
		/* Get the new position of the wheel to compare with previous values */
		kh4_get_position(&pos_left, &pos_right,dsPic);

		if((pos_left < (prevpos_left + IMOBIL_POS)) && (pos_left > (prevpos_left -IMOBIL_POS)) && (pos_right < (prevpos_right + IMOBIL_POS)) && (pos_right > (prevpos_right -IMOBIL_POS)))
		{
			
		  if(++immobility > 5)		  {
		  	#ifdef DEBUG
		  		 printf("immobility: %d\n",immobility);
		  	#endif	 
		     left_speed = RotSpeedL;
		     right_speed = RotSpeedR;

				 kh4_set_speed(left_speed ,right_speed ,dsPic );

				 do{
						usleep(1000);
						kh4_proximity_ir(Buffer, dsPic);
					}//while (((Buffer[2*2] | Buffer[2*2+1]<<8) >IMOBIL_SENS) || ((Buffer[3*2] | Buffer[3*2+1]<<8) >IMOBIL_SENS) || ((Buffer[4*2] | Buffer[4*2+1]<<8) >IMOBIL_SENS));
					while ( ((Buffer[3*2] | Buffer[3*2+1]<<8) >IMOBIL_SENS)); // front sensor

		     immobility = 0;
		     prevpos_left = pos_left;
		     prevpos_right = pos_right;
		  }
		}
		else
		{

		   immobility = 0;
		   prevpos_left = pos_left;
		   prevpos_right = pos_right;
		}

	//printf("lspd = %d rspd = %d\r\n", left_speed, right_speed); 			
		
   ioctl(porthandle, FIONREAD, &readable_size); // get number of bytes available to be read
  	
  	if (readable_size>0)
		{	
    	out=process_command(); // warning: if braitenberg 0 or 1, nested loop
   	} // if (readable_size>0)
  
  } while(!out);
  
  kh4_set_speed(0,0,dsPic ); // stop robot
  kh4_SetMode( kh4RegIdle,dsPic ); // set motors to idle
  
  // configure acceleration slope
  kh4_SetSpeedProfile(3,0,20 ,1,400,dsPic ); // Acceleration increment ,  Acceleration divider, Minimum speed 
  
  tcflush (porthandle, TCIFLUSH); // clear the read buffer
	fcntl(porthandle, F_SETFL, 0); // blocking input
  
  
  
  printf("Braitenberg mode exit\n");
  
}

#define RS232_EOA     	','
#define EOL_TEST(data) (data == '\r' || data == '\n' || data == '\0')

/*--------------------------------------------------------------------*/
/*! getArgs separate argument , return arguments number and save in larg every argument 
 *
 *	\param buf arguments string	
 *  \param larg array of argument
 *
 *  \return arguments number
*/ 
int getArgs(char *buf,string *larg)
{
	int narg=0;
	
	char delim[2]= {RS232_EOA , '\0'};
	char * pch;
	

		
	pch = strtok (buf,delim);
	while (pch != NULL)
	{
	  
	  strcpy(larg[narg],pch);
	  pch = strtok (NULL, delim);
	  
	  #ifdef DEBUG
		  printf(", | arg nb %d arg val: %s",narg,larg[narg]);
		#endif  

	  narg++;
	  
	  if (narg == MAX_ARG)
			break;
	}


	return narg;
}


/*--------------------------------------------------------------------*/
/*!  BinaryRead for GUI
 *
 *	\param narg number of argument	
 *  \param larg array of argument
 *
 *  \return A value :
 *      - 0 if success
 *      - <0 if any error
*/
int	BinaryRead(int narg,string *larg) {
	char Buffer[MAXBUFFERSIZE],buf[MAXBUFFERSIZE];
	int i, data,vsl,vsr;
		
		// Write the proximity sensor value in the buffer

		Buffer[0]='x';     // 0
		
		kh4_proximity_ir((char *)buf, dsPic);
		for (i=0;i<24;i++)  // 1-24
		{	
				Buffer[i+1]=buf[i+1];
		}	
		
		// Write the ambient light measurement 
	
		kh4_ambiant_ir((char *)buf, dsPic);
		for (i=0;i<24;i++)  // 25-48
		{
			Buffer[i+25]=buf[i+1];
		}		
		
				
		// Get the motor Speed and write it in the buffer
		kh4_get_speed(&vsl,&vsr,dsPic );  // 49-56
		
    Buffer[49]=(u_int8_t )(vsl & 0x00FF);
    Buffer[50]=(u_int8_t )((vsl>>8) & 0x00FF);
    Buffer[51]=(u_int8_t )((vsl>>16) & 0x00FF);
    Buffer[52]=(u_int8_t )((vsl>>24) & 0x00FF);
    

    Buffer[53]=(u_int8_t )(vsr & 0x00FF);
    Buffer[54]=(u_int8_t )((vsr>>8) & 0x00FF);
    Buffer[55]=(u_int8_t )((vsr>>16) & 0x00FF);
    Buffer[56]=(u_int8_t )((vsr>>24) & 0x00FF);

 
		
		// Get the motor Position and write it in the buffer
		
		kh4_get_position(&vsl,&vsr,dsPic ); // 57-64
 		Buffer[57]=(u_int8_t )(vsl & 0x00FF);
    Buffer[58]=(u_int8_t )((vsl>>8) & 0x00FF);
    Buffer[59]=(u_int8_t )((vsl>>16) & 0x00FF);
    Buffer[60]=(u_int8_t )((vsl>>24) & 0x00FF);
    Buffer[61]=(u_int8_t )(vsr & 0x00FF);
    Buffer[62]=(u_int8_t )((vsr>>8) & 0x00FF);
		Buffer[63]=(u_int8_t )((vsr>>16) & 0x00FF);
    Buffer[64]=(u_int8_t )((vsr>>24) & 0x00FF);
    
    // TODO: add accel or gyro?!
    
    Buffer[65]='\n';
    Buffer[66]='\r';
    Buffer[67]='\0';
		
		com_send(Buffer, sizeof(Buffer));
		
		#ifdef DEBUG
			printf("\nBinaryRead (hexa): ");
			for (i=0; i<66; i++)
				printf(" %02x",Buffer[i]);
		#endif	
						
		
	return 0;	
}		

/*--------------------------------------------------------------------*/
/*! process command
 *
 * \return A value : braitenberg end mode
 *    - >=0 if success
 *    - <0 if any error
*/
int process_command ()
{
	char Buffer[MAXBUFFERSIZE];
 	int narg;
  
  int out=0;
	
 	string larg[MAX_ARG];
	char *bptr;


	// receive and interpret commands (wait)
  if ( readLine(Buffer) >0 ) 
  {
  	#ifdef DEBUG
  		printf("%c length %d |%s|",Buffer[0],strlen(Buffer),Buffer);
  	#endif
  	
  	if (strlen(Buffer)>2)
  	{
  		/* Process all the args */
			bptr = Buffer + 2;
			
			narg=getArgs(bptr,larg);
			
		}
  	
		switch(Buffer[0])
		{
			case 'A':
				out=braitenberg(narg,larg);
				break;
			case 'B':
				revisionOS(narg,larg);
				break;
			case 'D': 
				SetSpeed(narg,larg);	
				break;
			case 'E': 
				GetSpeed(narg,larg);	
				break;
			case 'F': 
				SetTargetProfile(narg,larg);	
				break;
			case 'G': 
				GetUS(narg,larg);	
				break;
			case 'H': 
				ConfigPID(narg,larg);	
				break;
			case 'I': 
				ResetEncPosition(narg,larg);	
				break;
			case 'J': 
				ConfigSpeedProfile(narg,larg);	
				break;
			case 'K': 
				SetLED(narg,larg);	
				break;
			case 'L': 
				SetSpeedOpenLoop(narg,larg);	
				break;
			case 'M': 
				InitMot(narg,larg);	
				break;					
			case 'N': 
				ReadProxSensors(narg,larg);	
				break;
			case 'O': 
				ReadAmbSensors(narg,larg);	
				break;
			case 'P':
				ConfigPosMargin(narg,larg);	
				break;
			case 'R': 
				ReadPos(narg,larg);	
				break;
			case 'S':
				ReadGyro(narg,larg);
				break;
			case 'T':
				ReadAccel(narg,larg);
				break;		
			case 'U':
				ConfigUs(narg,larg);
				break;								
			case 'V':
				batStatus(narg,larg);
				break;
			case 'X':
				BinaryRead(narg,larg);
				break;
			case 'Z':
				ResetMicro(narg,larg);
				break;
			default:
				sprintf(Buffer,"%c\r\n",ERROR_CMD_CHAR);
				com_send(Buffer, strlen(Buffer));
				
		}
  }
      
	return out;
}


/*****************************************************************************/
/**** Main program ***********************************************************/
int main( int argc, char *argv[])
{
  char Buffer[MAXBUFFERSIZE];
 
 	
	
  printf("Khepera4 server program (C) K-Team S.A - modified in 2022 by @lharidonlouis\r\n");

	


  if(!initKH4())
  {
    printf("Init ok...\r\n");

   	kh4_revision((char *)Buffer, dsPic);
   	printf("\r\nVersion = %c, Revision = %u\r\n",
           (Buffer[0]>>4) +'A',Buffer[0] & 0x0F);


		if (argc == 2)
		{
			strcpy(Buffer,argv[1]); // use serial port given by parameter
		}
		else
		{
			strcpy(Buffer,SERIAL_PORT); // copy default
		}

		// open serial port
		if ((porthandle=com_connect(Buffer,BAUDRATE))<0)
		{
			printf("\nError: Serial port %s could not be open!\n",Buffer);
			return -1;
		}

		printf("\nParsing commands from serial port %s, baudrate %ld.\nPush CTRL-C for quitting!\n",Buffer,VAL_BAUDRATE);

		// loop
 		while (!quitReq) 
    {


			#ifdef DEBUG
      	printf("\n> ");
      #endif
			process_command();  

			
    }

    printf("Exiting...\r\n");
	}
	else
	  printf("Fatal error, unable to initialize\r\n");
	
	// close serial port	
	if (porthandle>=0)
		close(porthandle);
		  
	return 0;  
}


