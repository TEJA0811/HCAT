import {
  Controller,
  Get,
  Post,
  Body,
  Patch,
  Param,
  Delete,
  Put,
  ConflictException,
} from '@nestjs/common';
import { TeamsService } from './teams.service';
import { CreateTeamDto } from './dto/create-team.dto';
import { UpdateTeamDto } from './dto/update-team.dto';

@Controller('teams')
export class TeamsController {
  constructor(private readonly teamsService: TeamsService) {}

  @Post('create')
  async create(@Body() createTeamDto: CreateTeamDto) {
     const existingTeam = await this.teamsService.findBy({
          where: { team_name: createTeamDto.team_name,
           },
        });
    
        if (existingTeam) {
          throw new ConflictException('Team with this name already exists');
        }
    const team = await this.teamsService.create(createTeamDto);
    return {
      message: 'Team added successfully',
      data: team,
    };
  }

  @Get()
  async findAll() {
    const team = await this.teamsService.findAll();
    return {
      message: 'Team list',
      data: team,
    };
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    const team = await this.teamsService.findone(+id);
    if (!team) {
      return {
        message: 'Team not found',
        data: {},
      };
    }
    return {
      message: 'Team found',
      data: team,
    };
  }

  @Put(':id')
  async update(@Param('id') id: string, @Body() updateTeamDto: UpdateTeamDto) {
    const team = await this.teamsService.findone(+id);

    if (!team) {
      return {
        message: 'team not found',
        data: {},
      };
    }
    await this.teamsService.update(+id, updateTeamDto);
    return {
      message: 'Team updated successfully',
      data: team,
    };
  }

  @Delete(':id')
  async remove(@Param('id') id: string) {
    const team = await this.teamsService.findone(+id);

    if (!team) {
      return {
        message: 'team not found',
        data: {},
      };
    }
    await this.teamsService.remove(+id);
    return {
      message: 'Team updated successfully',
      data: team,
    };
  }
}
