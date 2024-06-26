/**
 * Head of code common to all C targets
 **/

#include "beremiz.h"
#include <string.h>
/*
 * Prototypes of functions provided by generated C softPLC
 **/
void config_run__(unsigned long tick);
void config_init__(void);


/*
 * Prototypes of functions provided by RTE
 * */
// void __init_debug(void);
// void __cleanup_debug(void);
// void __publish_debug(void);

/*
 *  Variables used by generated C softPLC and plugins
 **/
unsigned long __tick = 0;
char *PLC_ID = "PLCF407VE";

/*
 *  Variable generated by C softPLC and plugins
 **/
extern unsigned long greatest_tick_count__;

/* Help to quit cleanly when init fail at a certain level */
static int init_level = 0;


/*
 * Prototypes of functions exported by plugins
 **/
%(calls_prototypes)s


void __run(void)
{
    __tick++;

  // Altered to bypass __aeabi_uidivmod by directly resetting __tick, avoiding division/modulo operations.
  if (greatest_tick_count__ > 0 && __tick >= greatest_tick_count__) {
        __tick = 0;
    }

    %(retrieve_calls)s

    config_run__(__tick);

    // __publish_debug();

    %(publish_calls)s

}

/*
 * Initialize variables according to PLC's default values,
 * and then init plugins with that values
 **/
int __init(int argc,char **argv)
{
    int res = 0;
    init_level = 0;
    
    /* Effective tick time with 1ms default value */
    if(!common_ticktime__)
        common_ticktime__ = 1000000;

    config_init__();
    // __init_debug();
    %(init_calls)s
    return res;
}

/*
 * Calls plugin cleanup proc.
 **/
void __cleanup(void)
{
    %(cleanup_calls)s
    // __cleanup_debug();
}