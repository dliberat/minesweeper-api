class Tile {
    constructor(value, parent) {
      this.val = value;
      this.parent = parent;
    }
    isMine() {
      return this.val%2 === 1;
    }
    isVisible() {
      return (this.val>>1)%2 === 1;
    }
    isFlag() {
        return (this.val>>2) % 2 == 1;
    }
    neighboringMineCount() {
      return (this.val>>3);
    }
    displayText() {
      const neighborCount = this.neighboringMineCount();
      if (this.isVisible() && this.isMine()) {
        return '✕';
      }
      if (!this.isVisible() && this.isFlag()) {
        return '?'
      }
      if (!this.isVisible() || neighborCount === 0) {
        return '';
      }
      return neighborCount;
    }
    displayStyle() {
      const neighborCount = this.neighboringMineCount();
      if (this.isMine() && this.isVisible()) {
        return 'background-color: #f00';
      } else if (neighborCount <= 1) {
        return 'color: #404660';
      } else if (neighborCount === 2) {
        return 'color: #4bb88e';
      } else if (neighborCount === 3) {
        return 'color: #ff0000';
      } else {
        return 'color: #995eff';
      }
    }
    render(row, col) {
      const td = $("<td>");
      td.attr("id", `tile--${row}-${col}`);
      td.attr("style", this.displayStyle());
      td.addClass("tile");


      if (!this.isVisible()) {
        td.addClass("covered");

        if (this.parent.status === Game.STATUS_RUNNING) {
          td.addClass("hoverable");
          td.on("click", this.handleReveal, false);
          td.on("contextmenu", this.handleFlag, false);
        }
      }

      td.text(this.displayText());
      return td
    }
    handleReveal(e) {
      console.log('Revealing tile');
      return false;
    }
    handleFlag(e) {
      console.log('Flagging tile');
      return false;
    }
  }
