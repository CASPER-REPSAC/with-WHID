let date = new Date();
const renderCalender = () => {
    const viewYear = date.getFullYear();
    const viewMonth = date.getMonth();

    document.querySelector('.year').textContent = `${viewYear}`;
    document.querySelector('.month').textContent = `${viewMonth + 1}`;

    const prevLast = new Date(viewYear, viewMonth, 0);
    const thisLast = new Date(viewYear, viewMonth + 1, 0);

    const PLDate = prevLast.getDate();
    const PLDay = prevLast.getDay();

    const TLDate = thisLast.getDate();
    const TLDay = thisLast.getDay();

    const prevDates = [];
    const thisDates = [...Array(TLDate + 1).keys()].slice(1);
    const nextDates = [];

    if (PLDay !== 6) {
        for (let i = 0; i < PLDay + 1; i++) {
            prevDates.unshift(PLDate - i);
        }
    }

    for (let i = 1; i < 7 - TLDay; i++) {
        nextDates.push(i);
    }
    
    const arrrrr = data.split(',')

    const dates = prevDates.concat(thisDates, nextDates);
    const firstDateIndex = dates.indexOf(1);
    const lastDateIndex = dates.lastIndexOf(TLDate);
    dates.forEach((date, i) => {
        const condition = i >= firstDateIndex && i < lastDateIndex + 1 ?
            'this' :
            'other';
        let parse_date =  arrrrr[4].slice(53) + arrrrr[5] + arrrrr[6]
        let currnet_date = String(viewYear) +" "+ String(viewMonth+1) +" "+ String(date)
        dates[i] = `
            <div class="date ${condition}">

                <div class="date-itm">
                    ${date}
                </div>

                <div class="date_event">
                    <div class="event-itm">
                     ⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺⎺<br>
                     ${arrrrr[4].split('(')[1]}-${arrrrr[5]}-${arrrrr[6]} 
                    <a href=/calendardetail/${arrrrr[2]}>${(currnet_date == parse_date ? "[과제] "+String(arrrrr[2].split(":")[1]) : '')}</a>
                    </div>
                </div>

            </div>
        `;
    });

    document.querySelector('.dates').innerHTML = dates.join('');

    const today = new Date();
    if (viewMonth === today.getMonth() && viewYear === today.getFullYear()) {
        for (let date of document.querySelectorAll('.date-itm')) {
            if (+date.innerText === today.getDate()) {
                date.parentNode.classList.add('today');
                break;

            }
        }
    }
};

renderCalender();

const prevMonth = () => {
    date.setMonth(date.getMonth() - 1);
    renderCalender();
};

const nextMonth = () => {
    date.setMonth(date.getMonth() + 1);
    renderCalender();
};

const goToday = () => {
    date = new Date();
    renderCalender();
};